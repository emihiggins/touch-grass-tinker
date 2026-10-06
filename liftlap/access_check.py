"""Non-billable Tinker capabilities probe; run via Gateway protected egress.

No raw response/error body, headers, URLs from exceptions, or credentials are logged.
"""
import json
import os
import urllib.error
import urllib.request

URL = 'https://tinker.thinkingmachines.dev/services/tinker-prod/api/v1/get_server_capabilities'

class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None

def check(opener=None):
    key = os.environ.get('TINKER_API_KEY')
    if not key:
        return {'status': 'missing_credential', 'verified': False}
    # Fixed HTTPS destination, no redirects, inherited proxy/CA configuration.
    request = urllib.request.Request(URL, headers={'X-API-Key': key,
        'User-Agent': 'liftlap-access-check/0.1', 'Accept': 'application/json'})
    opener = opener or urllib.request.build_opener(NoRedirect())
    try:
        with opener.open(request, timeout=20) as response:
            if response.status != 200:
                return {'status': 'unexpected_http_status', 'http_status': response.status, 'verified': False}
            data = json.loads(response.read(1_000_001))
            models = data.get('supported_models') if isinstance(data, dict) else None
            if not isinstance(models, list):
                return {'status': 'unexpected_schema', 'verified': False}
            return {'status': 'capabilities_access_ok', 'http_status': 200, 'verified': True,
                    'supported_model_count': len(models),
                    'qwen3_8b_listed': any(isinstance(m, dict) and m.get('model_name') == 'Qwen/Qwen3-8B' for m in models),
                    'billing_verified': False}
    except urllib.error.HTTPError as e:
        e.close()
        return {'status': 'authentication_rejected' if e.code == 401 else 'http_error',
                'http_status': e.code, 'verified': False}
    except (ValueError, UnicodeError):
        return {'status': 'invalid_response', 'verified': False}
    except Exception:
        return {'status': 'transport_error', 'verified': False}

def main():
    result = check()
    print(json.dumps(result, sort_keys=True))
    raise SystemExit(0 if result['verified'] else 1)

if __name__ == '__main__': main()
