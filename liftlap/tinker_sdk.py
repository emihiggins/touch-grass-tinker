"""Pinned Tinker SDK read-only smoke using Gateway-owned credential substitution.

Uses a version-guarded private auth seam, not a plaintext key workaround.
No training/sampling methods are exposed by this command.
"""
import asyncio
import json
import os
import ssl

BASE_URL='https://tinker.thinkingmachines.dev/services/tinker-prod'
SDK_VERSION='0.32.0'

def make_client(transport=None):
    import httpx
    import tinker
    from tinker._client import AsyncTinker
    from tinker.lib._auth_token_provider import AuthTokenProvider
    if tinker.__version__ != SDK_VERSION:
        raise RuntimeError('SDK version mismatch; revalidate private auth integration')
    sentinel=os.environ.get('TINKER_API_KEY','')
    if not sentinel.startswith('oc-sent-v2.') or not sentinel.endswith('.end'):
        raise RuntimeError('Gateway protected credential required')
    if not os.environ.get('HTTPS_PROXY'):
        raise RuntimeError('Gateway egress proxy required')
    class GatewayAuth(AuthTokenProvider):
        async def get_token(self): return sentinel
    http=httpx.AsyncClient(verify=ssl.create_default_context(),trust_env=True,
                           follow_redirects=False,timeout=20,transport=transport)
    return AsyncTinker(base_url=BASE_URL,_auth=GatewayAuth(),http_client=http,max_retries=0)

async def check():
    try:
        async with make_client() as client:
            result=await client.service.get_server_capabilities()
            models=[m if isinstance(m,dict) else m.model_dump() for m in result.supported_models]
            return {'verified':True,'sdk_version':SDK_VERSION,'supported_model_count':len(models),
                    'qwen3_8b_listed':any(isinstance(m,dict) and m.get('model_name')=='Qwen/Qwen3-8B' for m in models),
                    'billing_verified':False,'scope':'read_only_sdk_capabilities'}
    except Exception as error:
        # Do not expose SDK exception bodies/headers; they may contain credentials.
        code=getattr(error,'status_code',None)
        return {'verified':False,'sdk_version':SDK_VERSION,'http_status':code if type(code) is int else None,
                'status':'sdk_access_failed','scope':'read_only_sdk_capabilities'}

if __name__=='__main__':
    result=asyncio.run(check());print(json.dumps(result,sort_keys=True))
    raise SystemExit(0 if result['verified'] else 1)
