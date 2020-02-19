import graphene

from django_server.graphene.space import SpaceMutation
from django_server.graphene.program import ProgramMutation
from django_server.graphene.user import UserMutation


class Mutation(SpaceMutation,
               ProgramMutation,
               UserMutation,
               graphene.ObjectType):
    pass
