import graphene

from django_server import const

ManClass = graphene.Enum.from_enum(const.ManClassEnum)
ProgramState = graphene.Enum.from_enum(const.ProgramStateEnum)
SpaceState = graphene.Enum.from_enum(const.SpaceStateEnum)
UserStatus = graphene.Enum.from_enum(const.UserStatusEnum)
ProgramTagType = graphene.Enum.from_enum(const.ProgramTagTypeEnum)


class Error(graphene.ObjectType):
    key = graphene.Field(graphene.Enum.from_enum(const.MannaError), required=True)
    message = graphene.String()

    def __str__(self):
        return f"{self.key} {self.message} {self.field} {self.info}"
