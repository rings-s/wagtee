# middleware.py - WebSocket authentication middleware
import jwt
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.conf import settings
from django.db import close_old_connections
from channels.middleware import BaseMiddleware
from channels.db import database_sync_to_async
from urllib.parse import parse_qs
import logging

User = get_user_model()
logger = logging.getLogger(__name__)

@database_sync_to_async
def get_user_from_token(token):
    """Get user from JWT token"""
    try:
        # Decode JWT token
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        user_id = payload.get('user_id')
        
        if user_id:
            user = User.objects.get(id=user_id)
            return user
    except (jwt.ExpiredSignatureError, jwt.DecodeError, User.DoesNotExist) as e:
        logger.warning(f"WebSocket authentication failed: {e}")
    
    return AnonymousUser()

class JWTAuthMiddleware(BaseMiddleware):
    """JWT authentication middleware for WebSocket connections"""
    
    async def __call__(self, scope, receive, send):
        # Close old database connections
        close_old_connections()
        
        # Get token from query string
        query_string = parse_qs(scope['query_string'].decode())
        token = query_string.get('token', [None])[0]
        
        if token:
            scope['user'] = await get_user_from_token(token)
        else:
            # Try to get token from headers
            headers = dict(scope.get('headers', []))
            auth_header = headers.get(b'authorization')
            
            if auth_header:
                try:
                    token = auth_header.decode().split(' ')[1]
                    scope['user'] = await get_user_from_token(token)
                except (IndexError, UnicodeDecodeError):
                    scope['user'] = AnonymousUser()
            else:
                scope['user'] = AnonymousUser()
        
        return await super().__call__(scope, receive, send)

def JWTAuthMiddlewareStack(inner):
    """WebSocket middleware stack with JWT authentication"""
    return JWTAuthMiddleware(inner)