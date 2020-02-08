import graphene

from django_server.graphene.space import SpaceMutation


class Mutation(SpaceMutation,
               graphene.ObjectType):
    pass
