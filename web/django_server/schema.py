import graphene

from django_server.graphene.mutation import Mutation
from django_server.graphene.query import Query

schema = graphene.Schema(query=Query, mutation=Mutation)
