import graphene
from graphene_django import DjangoObjectType

from django_server import models


class Space(DjangoObjectType):
    class Meta:
        model = models.Space


class Building(DjangoObjectType):
    class Meta:
        model = models.Building


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


class SpaceQuery(graphene.ObjectType):
    space = graphene.Field(Space, id=graphene.ID(required=True))
    building = graphene.Field(Building, id=graphene.ID(required=True))

    @staticmethod
    def resolve_space(root, info, **kwargs):
        id = kwargs.get('id')
        return models.Space.objects.get(pk=id)

    @staticmethod
    def resolve_building(root, info, **kwargs):
        id = kwargs.get('id')
        return models.Building.objects.get(pk=id)


class SpaceMutation(graphene.ObjectType):
    create_building = CreateBuilding.Field()
