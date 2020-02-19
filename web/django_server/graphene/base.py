import graphene

from django_server import const

ManClass = graphene.Enum.from_enum(const.ManClassEnum)
ProgramState = graphene.Enum.from_enum(const.ProgramStateEnum)
SpaceState = graphene.Enum.from_enum(const.SpaceStateEnum)
UserStatus = graphene.Enum.from_enum(const.UserStatusEnum)
