import json
from flask import request, _request_ctx_stack, abort
from functools import wraps
from jose import jwt
from urllib.request import urlopen


AUTH0_DOMAIN = 'dev--s9qtz0w.us.auth0.com'
ALGORITHMS = ['RS256']
API_AUDIENCE = 'course'

## AuthError Exception
'''
AuthError Exception
A standardized way to communicate auth failure modes
'''
class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code


## Auth Header

'''
Get the header from the request, split bearer and the token, and return the
token part of the header

Raise an AuthError if no header is present, or the header is malformed
'''
def get_token_auth_header():
    auth_body = request.headers.get('Authorization', None)

    if auth_body is None:
        raise AuthError({
            'code': 'authorization_header_missing',
            'description': 'Authorization header is expected'
        }, 401)
    auth_strs = auth_body.split(' ')
    if auth_strs[0].lower() != 'bearer':
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Header must start with "Bearer"'
        }, 401)
    if len(auth_strs) == 1:
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Token is missing in the header'
        }, 401)
    if len(auth_strs) > 2:
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Authentication header must be "Bearer token"'
        }, 401)

    token = auth_strs[1]
    return token


'''
@INPUTS
    permission: string permission (i.e. 'post:drink')
    payload: decoded jwt payload

Raise an AuthError if permissions are not included in the payload, or the
requested permission string is not in the payload permissions array

Return true otherwise
'''
def check_permissions(permission, payload):
    if 'permissions' not in payload:
        raise AuthError({
            'code': 'invalid_claims',
            'description': '"permissions" not included in JWT'
        }, 400)
    if permission not in payload['permissions']:
        raise AuthError({
            'code': 'no_permission',
            'description': 'Requested permission not allowed'
        }, 403)
    return True


'''
@INPUTS
    token: a json web token (string), which shoud be an Auth0 token with key
    id (kid)

Verify the token using Auth0Domain/.well-known/jwks.json, decode the payload from
the token, validate the claims

Return the decoded payload
'''
def verify_decode_jwt(token):
    jsonurl = urlopen(f'https://{AUTH0_DOMAIN}/.well-known/jwks.json')
    jwks = json.loads(jsonurl.read())
    unverified_header = jwt.get_unverified_header(token)
    rsa_key = {}
    for key in jwks['keys']:
        if key['kid'] == unverified_header['kid']:
            rsa_key = {
                'kty': key['kty'],
                'kid': key['kid'],
                'use': key['use'],
                'n': key['n'],
                'e': key['e']
            }
    if len(rsa_key) == 0:
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Unable to find the appropriate key'
        }, 401)

    try:
        payload = jwt.decode(
            token,
            rsa_key,
            algorithms = ALGORITHMS,
            audience = API_AUDIENCE,
            issuer = f'https://{AUTH0_DOMAIN}/'
        )
        return payload

    except jwt.ExpiredSignatureError:
        raise AuthError({
            'code': 'token_expired',
            'description': 'Token is expired'
        }, 401)

    except jwt.JWTClaimsError:
        raise AuthError({
            'code': 'invalid_claims',
            'description': 'Incorrect claims,' +
                'please check the audience and issuer'
        }, 401)

    except Exception:
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Unable to parse the authentication token'
        }, 401)


'''
Decorator of requiring authorization of a specific permission

@INPUTS
    permission: string permission (i.e. 'post:course')

Use the get_token_auth_header method to get the token
Use the verify_decode_jwt method to decode the jwt
Use the check_permissions method validate claims and check the requested
permission

Return the decorator which passes the decoded payload to the decorated method
'''
def requires_auth(permission=''):
    def requires_auth_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            try:
                token = get_token_auth_header()
                payload = verify_decode_jwt(token)
                check_permissions(permission, payload)
            except AuthError as e:
                abort(e.status_code, description=e.error['description'])
            return f(payload, *args, **kwargs)
        return wrapper
    return requires_auth_decorator
