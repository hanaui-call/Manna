import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField

from django_server import const
from django_server import models
from django_server.graphene.base import ManClass, SpaceState
from django_server.graphene.utils import assign, has_building, has_space, get_object_from_global_id
from django_server.libs.authentification import authorization


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
    def resolve_state(root, info, **kwargs):
        return root.state

    @staticmethod
    def resolve_required_man_class(root, info, **kwargs):
        return root.required_man_class


class Building(DjangoObjectType):
    class Meta:
        model = models.Building
        filter_fields = {
            'name': ['exact', 'icontains'],
            'address': ['exact', 'icontains'],
        }
        interfaces = (graphene.Node,)


class Zoom(DjangoObjectType):
    class Meta:
        model = models.Zoom
        filter_fields = {
            'name': ['exact', 'icontains'],
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
    @authorization
    def mutate(root, info, **kwargs):
        name = kwargs.get('name')
        address = kwargs.get('address')
        detailed_address = kwargs.get('detailed_address', '')
        phone = kwargs.get('phone', '')
        user = info.context.user

        building = models.Building.objects.create(name=name,
                                                  address=address,
                                                  detailed_address=detailed_address,
                                                  phone=phone,
                                                  made_user=user)
        return CreateBuilding(building=building)


class UpdateBuilding(graphene.Mutation):
    building = graphene.Field(Building)

    class Arguments:
        id = graphene.ID(required=True)
        name = graphene.String()
        address = graphene.String()
        detailed_address = graphene.String()
        phone = graphene.String()

    @staticmethod
    @authorization
    @has_building
    def mutate(root, info, **kwargs):
        building = info.context.building

        assign(kwargs, building, 'name')
        assign(kwargs, building, 'address')
        assign(kwargs, building, 'detailed_address')
        assign(kwargs, building, 'phone')

        building.save()

        return UpdateBuilding(building=building)


class DeleteBuilding(graphene.Mutation):
    ok = graphene.Boolean()

    class Arguments:
        id = graphene.ID(required=True)

    @staticmethod
    @authorization
    @has_building
    def mutate(root, info, **kwargs):
        info.context.building.delete()
        return DeleteBuilding(ok=True)


class CreateSpace(graphene.Mutation):
    space = graphene.Field(Space)

    class Arguments:
        name = graphene.String(required=True)
        required_man_class = graphene.Argument(ManClass)
        state = graphene.Argument(SpaceState)
        building_id = graphene.ID(required=True)

    @staticmethod
    @authorization
    def mutate(root, info, **kwargs):
        name = kwargs.get('name')
        required_man_class = kwargs.get('required_man_class', const.ManClassEnum.NON_MEMBER.value)
        state = kwargs.get('state', const.SpaceStateEnum.WATING.value)
        building = get_object_from_global_id(models.Building, kwargs.get('building_id'))
        user = info.context.user

        space = models.Space.objects.create(name=name,
                                            building=building,
                                            required_man_class=required_man_class,
                                            state=state,
                                            made_user=user)

        return CreateSpace(space=space)


class UpdateSpace(graphene.Mutation):
    space = graphene.Field(Space)

    class Arguments:
        id = graphene.ID(required=True)
        name = graphene.String()
        required_man_class = graphene.Argument(ManClass)
        state = graphene.Argument(SpaceState)
        building_id = graphene.ID()

    @staticmethod
    @authorization
    @has_space
    def mutate(root, info, **kwargs):
        space = info.context.space

        assign(kwargs, space, 'name')
        assign(kwargs, space, 'required_man_class')
        assign(kwargs, space, 'state')

        building_id = kwargs.get('building_id')
        if building_id:
            building = get_object_from_global_id(models.Building, building_id)
            space.building = building

        space.save()

        return UpdateSpace(space=space)


class DeleteSpace(graphene.Mutation):
    ok = graphene.Boolean()

    class Arguments:
        id = graphene.ID(required=True)

    @staticmethod
    @authorization
    @has_space
    def mutate(root, info, **kwargs):
        info.context.space.delete()
        return DeleteSpace(ok=True)


class SpaceQuery(graphene.ObjectType):
    space = graphene.Field(Space, id=graphene.ID(required=True))
    building = graphene.Field(Building, id=graphene.ID(required=True))
    zoom = graphene.Field(Zoom, id=graphene.ID(required=True))
    all_spaces = DjangoFilterConnectionField(Space)
    all_buildings = DjangoFilterConnectionField(Building)
    all_zooms = DjangoFilterConnectionField(Zoom)

    @staticmethod
    def resolve_space(root, info, **kwargs):
        return get_object_from_global_id(models.Space, kwargs.get('id'))

    @staticmethod
    def resolve_building(root, info, **kwargs):
        return get_object_from_global_id(models.Building, kwargs.get('id'))

    @staticmethod
    def resolve_zoom(root, info, **kwargs):
        return get_object_from_global_id(models.Zoom, kwargs.get('id'))


class SpaceMutation(graphene.ObjectType):
    create_building = CreateBuilding.Field()
    create_space = CreateSpace.Field()
    update_building = UpdateBuilding.Field()
    update_space = UpdateSpace.Field()
    delete_building = DeleteBuilding.Field()
    delete_space = DeleteSpace.Field()
