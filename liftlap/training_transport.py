"""Pinned protected-client training transport; no CLI or automatic live launch.

Uses SDK request types and Cookbook-rendered Datums, not a custom training format.
Submission exceptions are terminal. Journaled futures may be inspected later, but
this adapter never retries a mutation or resumes an ambiguous optimizer step.
"""
import asyncio
import json
import os
from pathlib import Path

class TrainingTransport:
    def __init__(self,client,journal,*,polls=30,poll_interval=1):
        if type(polls) is not int or not 1<=polls<=60 or not 0<=poll_interval<=5:
            raise ValueError('Invalid polling bounds')
        self.client=client;self.polls=polls;self.interval=poll_interval
        self.journal=Path(journal)
        # An existing journal may describe completed or ambiguous mutations.
        with self.journal.open('x'):pass
        self.session=None;self.model=None;self.sequence=0;self.failed=False;self.model_sequence=0

    def record(self,event,**fields):
        with self.journal.open('a') as f:
            f.write(json.dumps({'event':event,**fields},sort_keys=True)+'\n');f.flush();os.fsync(f.fileno())

    async def operation(self,name,submit,response_type):
        if self.failed:raise RuntimeError('Transport halted; reconcile journal before any continuation')
        self.record('submission_start',operation=name,sequence=self.sequence)
        try:
            future=await submit()
            self.record('submitted',operation=name,request_id=future.request_id)
            from tinker.types.future_retrieve_request import FutureRetrieveRequest
            from tinker.proto.response_conv import deserialize_proto_response,PROTO_SUPPORTED_TYPES
            for attempt in range(self.polls):
                from tinker import APITimeoutError,APIStatusError
                try:
                    response=await self.client.futures.with_raw_response.retrieve(
                        request=FutureRetrieveRequest(request_id=future.request_id),timeout=45,max_retries=0,
                        extra_headers={'Accept':'application/x-protobuf' if response_type in PROTO_SUPPORTED_TYPES else 'application/json'})
                except (APITimeoutError,APIStatusError) as error:
                    if isinstance(error,APIStatusError) and error.status_code!=408:raise
                    self.record('read_timeout',operation=name,request_id=future.request_id)
                    if attempt+1==self.polls:raise
                    continue
                if 'application/x-protobuf' in response.http_response.headers.get('content-type',''):
                    result=deserialize_proto_response(response.http_response.content,response_type)
                    self.record('completed',operation=name,request_id=future.request_id)
                    return result
                body=await response.json()
                if body.get('type')!='try_again':
                    if 'error' in body or body.get('type') in ('request_failed','error'):raise RuntimeError('Provider future failed')
                    result=response_type.model_validate(body)
                    self.record('completed',operation=name,request_id=future.request_id)
                    return result
                if attempt+1<self.polls:await asyncio.sleep(self.interval)
            raise TimeoutError('Future polling limit reached')
        except BaseException as error:
            self.failed=True
            # No raw SDK errors, payloads, auth headers or tokens in journal.
            self.record('halted',operation=name,error_type=type(error).__name__)
            raise

    def next_sequence(self):
        self.sequence+=1;return self.sequence

    async def create(self,model_name,rank=16):
        import tinker
        from tinker import types
        if self.session is not None or self.failed:raise RuntimeError('Session already attempted or transport halted')
        self.record('session_start')
        try:
            session=await self.client.service.create_session(request=types.CreateSessionRequest(
                tags=['liftlap-training-smoke'],user_metadata={'project':'touch-grass-liftlap'},sdk_version=tinker.__version__))
            self.session=session.session_id
            self.record('session_created',session_id=self.session)
        except BaseException as error:
            self.failed=True;self.record('halted',operation='create_session',error_type=type(error).__name__);raise
        request=types.CreateModelRequest(session_id=self.session,model_seq_id=0,base_model=model_name,
            lora_config=types.LoraConfig(rank=rank,seed=20261006,train_mlp=True,train_attn=True,train_unembed=True))
        result=await self.operation('create_model',lambda:self.client.models.create(request=request),types.CreateModelResponse)
        self.model=result.model_id
        self.record('model_created',model_id=self.model)
        return self.model

    async def train_step(self,datums,learning_rate=0.0001):
        from tinker import types
        if not self.model or not datums:raise ValueError('Model and nonempty batch required')
        request=types.ForwardBackwardRequest(model_id=self.model,seq_id=self.next_sequence(),
            forward_backward_input=types.ForwardBackwardInput(data=datums,loss_fn='cross_entropy'))
        output=await self.operation('forward_backward',lambda:self.client.training.forward_backward(request=request),types.ForwardBackwardOutput)
        request=types.OptimStepRequest(model_id=self.model,seq_id=self.next_sequence(),optim_params=types.AdamParams(learning_rate=learning_rate))
        await self.operation('optim_step',lambda:self.client.training.optim_step(request=request),types.OptimStepResponse)
        return output

    async def checkpoint(self,name,*,sampler=False,ttl_seconds=3600):
        from tinker import types
        if not self.model or type(ttl_seconds) is not int or not 3600<=ttl_seconds<=86400:
            raise ValueError('Model required; checkpoint TTL must be 1–24 hours')
        if not name or '/' in name:raise ValueError('Simple checkpoint name required')
        if sampler:
            request=types.SaveWeightsForSamplerRequest(model_id=self.model,path=name,seq_id=self.next_sequence(),ttl_seconds=ttl_seconds)
            result=await self.operation('save_sampler',lambda:self.client.weights.save_for_sampler(request=request,max_retries=0),types.SaveWeightsForSamplerResponse)
        else:
            request=types.SaveWeightsRequest(model_id=self.model,path=name,seq_id=self.next_sequence(),ttl_seconds=ttl_seconds,overwrite=False)
            result=await self.operation('save_state',lambda:self.client.weights.save(request=request,max_retries=0),types.SaveWeightsResponse)
        if not result.path.startswith('tinker://'):
            self.failed=True;raise ValueError('Invalid checkpoint URI')
        self.record('checkpoint_saved',path=result.path,ttl_seconds=ttl_seconds,sampler=sampler)
        return result.path

    async def restore(self,path):
        from tinker import types
        if not self.model or not path.startswith('tinker://'):raise ValueError('Model and checkpoint URI required')
        if not self.session:raise ValueError('Session required for fresh-model restore')
        self.model_sequence+=1
        request=types.LoadWeightsRequest(session_id=self.session,model_seq_id=self.model_sequence,path=path,optimizer=True)
        result=await self.operation('restore_state',lambda:self.client.weights.load(request=request),types.LoadWeightsResponse)
        expected=f'{self.session}:train:{self.model_sequence}'
        if result.model_id not in (None,expected):
            self.failed=True;raise ValueError('Unexpected restored model identity')
        self.model=expected;self.sequence=0
        self.record('optimizer_restore_completed',path=path)
        return result
