import logging
from collections import namedtuple

import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql_relay.node.node import from_global_id

from django_server import const
from django_server import models

Rid = namedtuple('Rid', 'name id')

logger = logging.getLogger('__file__')

ManClass = graphene.Enum.from_enum(const.ManClassEnum)
SpaceState = graphene.Enum.from_enum(const.SpaceStateEnum)


class Space(DjangoObjectType):
    state = graphene.Field(SpaceState)
    required_man_class = graphene.Field(ManClass)

    class Meta:
        model = models.Space
        filter_fields = {
            'name': ['exact', 'icontains'],
        }
        interfaces = (graphene.Node,)
        exclude_fields = ('state', 'required_man_class')

    @staticmethod
    def resove_state(root, info, **kwargs):
        return root.state

    @staticmethod
    def resove_required_man_class(root, info, **kwargs):
        return root.required_man_class


class Building(DjangoObjectType):
    class Meta:
        model = models.Building
        filter_fields = {
            'name': ['exact', 'icontains'],
            'address': ['exact', 'icontains'],
        }
        interfaces = (graphene.Node,)


class CreateBuilding(graphene.Mutation):
    building = graphene.Field(Building)

    class Arguments:
        name = graphene.String(required=True)
        address = graphene.String(required=True)
        detailed_address = graphene.String()
        phone = graphene.String()

    @staticmethod
    def mutate(root, info, **kwargs):
        name = kwargs.get('name')
        address = kwargs.get('address')
        detailed_address = kwargs.get('detailed_address', '')
        phone = kwargs.get('phone', '')

        # FIXME
        user = models.Profile.objects.first()

        building = models.Building.objects.create(name=name,
                                                  address=address,
                                                  detailed_address=detailed_address,
                                                  phone=phone,
                                                  made_user=user)
        return CreateBuilding(building=building)


class CreateSpace(graphene.Mutation):
    space = graphene.Field(Space)

    class Arguments:
        name = graphene.String(required=True)
        required_man_class = graphene.Argument(ManClass)
        state = graphene.Argument(SpaceState)
        building_id = graphene.ID(required=True)

    @staticmethod
    def mutate(root, info, **kwargs):
        name = kwargs.get('name')
        required_man_class = kwargs.get('required_man_class', const.ManClassEnum.NON_MEMBER.value)
        state = kwargs.get('state', const.SpaceStateEnum.WATING.value)
        building_id = kwargs.get('building_id')
        building = models.Building.objects.get(pk=building_id)

        # FIXME
        user = models.Profile.objects.first()
        space = models.Space.objects.create(name=name,
                                            building=building,
                                            required_man_class=required_man_class,
                                            state=state,
                                            made_user=user)

        return CreateSpace(space=space)


class SpaceQuery(graphene.ObjectType):
    space = graphene.Field(Space, id=graphene.ID(required=True))
    building = graphene.Field(Building, id=graphene.ID(required=True))
    all_spaces = DjangoFilterConnectionField(Space)
    all_buildings = DjangoFilterConnectionField(Building)

    @staticmethod
    def resolve_space(root, info, **kwargs):
        rid = Rid(*from_global_id(kwargs.get('id')))
        return models.Space.objects.get(pk=rid.id)

    @staticmethod
    def resolve_building(root, info, **kwargs):
        rid = Rid(*from_global_id(kwargs.get('id')))
        return models.Building.objects.get(pk=rid.id)


class SpaceMutation(graphene.ObjectType):
    create_building = CreateBuilding.Field()
    create_space = CreateSpace.Field()
