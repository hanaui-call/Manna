import graphene
from graphene_django import DjangoObjectType

from django_server import const
from django_server import models

ManClass = graphene.Enum.from_enum(const.ManClassEnum)
ProgramState = graphene.Enum.from_enum(const.ProgramStateEnum)
SpaceState = graphene.Enum.from_enum(const.SpaceStateEnum)
UserStatus = graphene.Enum.from_enum(const.UserStatusEnum)
ProgramTagType = graphene.Enum.from_enum(const.ProgramTagTypeEnum)


def is_editable_program(program, user):
    if user.role == const.ManClassEnum.ADMIN.value:
        return True

    return program.owner == user


class Program(DjangoObjectType):
    state = graphene.Field(ProgramState)
    required_man_class = graphene.Field(ManClass)
    is_editable = graphene.Boolean()

    class Meta:
        model = models.Program
        filter_fields = {
            'name': ['exact', 'icontains'],
            'description': ['exact', 'icontains'],
        }
        interfaces = (graphene.Node,)
        exclude_fields = ('state', 'required_man_class')

    @staticmethod
    def resolve_state(root, info, **kwargs):
        return root.state

    @staticmethod
    def resolve_required_man_class(root, info, **kwargs):
        return root.required_man_class

    @staticmethod
    def resolve_is_editable(root, info, **kwargs):
        if not hasattr(info.context, 'user'):
            return False
        return is_editable_program(root, info.context.user)


class Meeting(DjangoObjectType):
    class Meta:
        model = models.Meeting
        filter_fields = {
            'name': ['exact', 'icontains'],
        }
        interfaces = (graphene.Node,)


class Error(graphene.ObjectType):
    key = graphene.Field(graphene.Enum.from_enum(const.MannaError), required=True)
    message = graphene.String()

    def __str__(self):
        return f"{self.key} {self.message} {self.field} {self.info}"
