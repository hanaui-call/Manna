import graphene

from django_server.graphene.user import UserQuery
from django_server.graphene.space import SpaceQuery
from django_server.graphene.program import ProgramQuery


class Query(UserQuery,
            SpaceQuery,
            ProgramQuery,
            graphene.ObjectType):
    pass
