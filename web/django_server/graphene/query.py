import graphene

from django_server.graphene.user import UserQuery
from django_server.graphene.space import SpaceQuery


class Query(UserQuery,
            SpaceQuery,
            graphene.ObjectType):
    pass
