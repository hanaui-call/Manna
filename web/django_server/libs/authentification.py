import datetime
import logging
from datetime import timedelta
from functools import wraps

import jwt
from dateutil import parser
from graphene_django.views import GraphQLView

from django_server.graphene.exception import PermissionException
from django_server.models import Profile
from django_server.settings import SECRET_KEY

TOKEN_VALID_DAYS = 365

logger = logging.getLogger(__name__)


def authorization(func):
    @wraps(func)
    def wrap(root, info, **kwargs):
        if not hasattr(info.context, 'user'):
            raise PermissionException(message="Invalid auth token")

        user = info.context.user
        try:
            user = Profile.objects.get(id=user.id)  # reload
        except Profile.DoesNotExist:
            raise PermissionException(message="Invalid agent")

        info.context.user = user
        return func(root, info, **kwargs)

    return wrap


class TokenAuthGraphQLView(GraphQLView):
    def dispatch(self, request, *args, **kwargs):
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        ret = AuthHelper.decode_token(auth_header)[0]

        if ret:
            user_id = ret.get('user_id')
            expires = ret.get('expires')

            try:
                profile = Profile.objects.get(id=user_id)
                logger.debug(f"Login successful {profile}")
                setattr(request, 'user', profile)
                setattr(request, 'expires', expires)
            except Exception:
                pass

        return super().dispatch(request, *args, **kwargs)


class AuthHelper(object):
    @staticmethod
    def _generate_token(payload):
        now = datetime.datetime.utcnow()
        expire_at = now + timedelta(days=TOKEN_VALID_DAYS)
        payload["expires"] = str(expire_at)
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256').decode('utf-8')
        return token

    @staticmethod
    def generate_token(payload):
        logger.debug(f"generate_token: payload={payload}")
        user_id = payload.get('user_id')

        if not user_id:
            logger.error("fail to generate token. user_id is None")
            return None

        try:
            Profile.objects.get(id=user_id)
        except Profile.DoesNotExist:
            logger.error("fail to generate token. NO User")
            return None

        return AuthHelper._generate_token(payload)

    @staticmethod
    def decode_token(token):
        try:
            result = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            logger.debug("decode token {}".format(result))
            expires = result.get('expires')
            if not expires:
                return None, "token is malformed"

            now = datetime.datetime.utcnow()
            expire_at = parser.parse(expires)
            if expire_at < now:
                return None, "token is expired"
            return result, None

        except Exception as ex:
            logger.exception(ex)
            return None, "token is not correct"
