import logging

import graphene

from django_server import const

logger = logging.getLogger('__file__')

ManClass = graphene.Enum.from_enum(const.ManClassEnum)
ProgramState = graphene.Enum.from_enum(const.ProgramStateEnum)
SpaceState = graphene.Enum.from_enum(const.SpaceStateEnum)

