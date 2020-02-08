import graphene
from graphene_django import DjangoObjectType

from django_server import models


class Profile(DjangoObjectType):
    name = graphene.String(required=True)
    email = graphene.String(required=True)

    class Meta:
        model = models.Profile

    @staticmethod
    def resolve_name(root, info):
        return f'{root.user.last_name}{root.user.first_name}'

    @staticmethod
    def resolve_email(root, info):
        return root.user.email


class UserQuery(graphene.ObjectType):
    user = graphene.Field(Profile)

    @staticmethod
    def resolve_user(root, info, **kwargs):
        return models.Profile.objects.first()
