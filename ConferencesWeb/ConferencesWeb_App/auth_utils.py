import base64
import json
from datetime import datetime, timedelta
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from .rsa_utils import encrypt_rsa, decrypt_rsa, generate_rsa_keys
import redis

public_key, private_key = generate_rsa_keys()
blacklist = redis.StrictRedis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0)

def encode_jwt(payload, secret, expires_in=10):
    header = json.dumps({"alg": "RS256", "typ": "JWT"}).encode()
    payload['exp'] = (datetime.utcnow() + timedelta(seconds=expires_in)).timestamp()
    payload = json.dumps(payload).encode()
    segments = [
        base64.urlsafe_b64encode(header).rstrip(b'='),
        base64.urlsafe_b64encode(payload).rstrip(b'='),
    ]
    signing_input = b'.'.join(segments)
    signature = encrypt_rsa(signing_input.decode(), public_key)
    segments.append(base64.urlsafe_b64encode(str(signature).encode()).rstrip(b'='))
    return b'.'.join(segments).decode()

def decode_jwt(token, secret):
    if blacklist.get(token):
        raise ValueError("Token is blacklisted")

    segments = token.split('.')
    if len(segments) != 3:
        raise ValueError("Invalid token")

    header = base64.urlsafe_b64decode(segments[0] + '==')
    payload = base64.urlsafe_b64decode(segments[1] + '==')
    signature = base64.urlsafe_b64decode(segments[2] + '==').decode()

    signing_input = '.'.join(segments[:2]).encode()
    expected_signature = decrypt_rsa(int(signature), private_key)

    if signing_input.decode() != expected_signature:
        raise ValueError("Invalid signature")

    payload_data = json.loads(payload)
    if datetime.utcnow().timestamp() > payload_data['exp']:
        raise ValueError("Token has expired")

    return payload_data

def getUserByToken(request):
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return AnonymousUser()
    token = auth_header.split(' ')[1]
    try:
        payload = decode_jwt(token, settings.SECRET_KEY)
        user = get_user_model().objects.get(id=payload['user_id'])
    except (ValueError, get_user_model().DoesNotExist):
        user = AnonymousUser()
    return user

def blacklist_token(token):
    blacklist.set(token, "blacklisted")

def create_refresh_token(payload, secret, expires_in=604800):
    return encode_jwt(payload, secret, expires_in)

def decode_refresh_token(token, secret):
    return decode_jwt(token, secret)
