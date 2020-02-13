import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField

from django_server import const
from django_server import models
from django_server.graphene.base import ManClass, ProgramState, logger
from django_server.graphene.utils import get_object_from_global_id, has_program, assign


class Program(DjangoObjectType):
    state = graphene.Field(ProgramState)
    required_man_class = graphene.Field(ManClass)

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


class CreateProgram(graphene.Mutation):
    program = graphene.Field(Program)

    class Arguments:
        name = graphene.String(required=True)
        description = graphene.String()
        space_id = graphene.ID()
        state = graphene.Argument(ProgramState)
        participants = graphene.List(graphene.ID)
        participants_min = graphene.Int()
        participants_max = graphene.Int()
        required_man_class = graphene.Argument(ManClass)
        open_time = graphene.types.datetime.DateTime(required=True)
        close_time = graphene.types.datetime.DateTime()

    @staticmethod
    def mutate(root, info, **kwargs):
        name = kwargs.get('name')
        description = kwargs.get('description', '')
        space = get_object_from_global_id(models.Space, kwargs.get('space_id'))
        state = kwargs.get('state', const.SpaceStateEnum.WATING.value)
        participants_min = kwargs.get('participants_min', 1)
        participants_max = kwargs.get('participants_max', 10)
        required_man_class = kwargs.get('required_man_class', const.ManClassEnum.NON_MEMBER.value)
        open_time = kwargs.get('open_time')
        close_time = kwargs.get('close_time')

        # FIXME
        user = models.Profile.objects.first()
        program = models.Program.objects.create(name=name,
                                                description=description,
                                                space=space,
                                                state=state,
                                                participants_max=participants_max,
                                                participants_min=participants_min,
                                                required_man_class=required_man_class,
                                                open_time=open_time,
                                                close_time=close_time,
                                                owner=user)

        return CreateProgram(program=program)


class UpdateProgram(graphene.Mutation):
    program = graphene.Field(Program)

    class Arguments:
        id = graphene.ID(required=True)
        name = graphene.String()
        description = graphene.String()
        space_id = graphene.ID()
        state = graphene.Argument(ProgramState)
        participants_min = graphene.Int()
        participants_max = graphene.Int()
        required_man_class = graphene.Argument(ManClass)
        open_time = graphene.types.datetime.DateTime()
        close_time = graphene.types.datetime.DateTime()

    @staticmethod
    @has_program
    def mutate(root, info, **kwargs):
        program = info.context.program

        assign(kwargs, program, 'name')
        assign(kwargs, program, 'description')
        assign(kwargs, program, 'state')
        assign(kwargs, program, 'participants_min')
        assign(kwargs, program, 'participants_max')
        assign(kwargs, program, 'required_man_class')
        assign(kwargs, program, 'open_time')
        assign(kwargs, program, 'close_time')

        space_id = kwargs.get('space_id')
        if space_id:
            space = get_object_from_global_id(models.Space, space_id)
            program.space = space

        program.save()

        return UpdateProgram(program=program)


class DeleteProgram(graphene.Mutation):
    ok = graphene.Boolean()

    class Arguments:
        id = graphene.ID(required=True)

    @staticmethod
    @has_program
    def mutate(root, info, **kwargs):
        info.context.program.delete()
        return DeleteProgram(ok=True)


class ProgramQuery(graphene.ObjectType):
    program = graphene.Field(Program, id=graphene.ID(required=True))
    all_programs = DjangoFilterConnectionField(Program)

    @staticmethod
    @has_program
    def resolve_program(root, info, **kwargs):
        return info.context.program


class ProgramMutation(graphene.ObjectType):
    create_program = CreateProgram.Field()
    update_program = UpdateProgram.Field()
    delete_program = DeleteProgram.Field()
