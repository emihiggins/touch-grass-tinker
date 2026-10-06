"""Read-only billing visibility check. Never creates sessions, training or samples."""
import asyncio,json
from .tinker_sdk import make_client

async def check():
    try:
        from tinker import types
        async with make_client() as client:
            result=await client.get('/api/v1/billing/usage/events',options={'params':{
                'starting_on':'2026-10-05T00:00:00Z','ending_before':'2026-10-07T00:00:00Z'}},cast_to=types.BillingUsageResponse)
        data=result.model_dump(mode='json',warnings=False) if hasattr(result,'model_dump') else {}
        # Deliberately omit account identities, raw org/project IDs and event payloads.
        return {'scope':'read_only_billing_visibility_not_credit_balance_or_project_reconciliation',
                'billing_endpoint_accessible':True,'response_fields':sorted(data),
                'account_credits_verified':False,'provider_calls_creating_compute':0,
                'note':'Billing data may lag; availability alone does not reconcile current usage or show remaining credits.'}
    except Exception as error:
        code=getattr(error,'status_code',None)
        return {'scope':'read_only_billing_visibility','billing_endpoint_accessible':False,
                'http_status':code if type(code) is int else None,'error_type':type(error).__name__,
                'account_credits_verified':False,'provider_calls_creating_compute':0}
if __name__=='__main__':print(json.dumps(asyncio.run(check()),indent=2))
