import graphene

from django_server.graphene.space import SpaceMutation
from django_server.graphene.program import ProgramMutation


class Mutation(SpaceMutation,
               ProgramMutation,
               graphene.ObjectType):
    pass
