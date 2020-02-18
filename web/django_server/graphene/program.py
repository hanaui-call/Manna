import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField

from django_server import const
from django_server import models
from django_server.graphene.base import ManClass, ProgramState
from django_server.graphene.utils import get_object_from_global_id, has_program, assign, has_meeting


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


class Meeting(DjangoObjectType):
    class Meta:
        model = models.Meeting
        filter_fields = {
            'name': ['exact', 'icontains'],
        }
        interfaces = (graphene.Node,)


class CreateProgram(graphene.Mutation):
    program = graphene.Field(Program)

    class Arguments:
        name = graphene.String(required=True)
        description = graphene.String()
        space_id = graphene.ID()
        state = graphene.Argument(ProgramState)
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


class CreateMeeting(graphene.Mutation):
    meeting = graphene.Field(Meeting)

    class Arguments:
        name = graphene.String(required=True)
        program_id = graphene.ID(required=True)
        start_time = graphene.types.datetime.DateTime(required=True)
        end_time = graphene.types.datetime.DateTime(required=True)

    @staticmethod
    def mutate(root, info, **kwargs):
        name = kwargs.get('name')
        program = get_object_from_global_id(models.Program, kwargs.get('program_id'))
        start_time = kwargs.get('start_time')
        end_time = kwargs.get('end_time')

        meeting = models.Meeting.objects.create(name=name,
                                                program=program,
                                                start_time=start_time,
                                                end_time=end_time)

        return CreateMeeting(meeting=meeting)


class UpdateMeeting(graphene.Mutation):
    meeting = graphene.Field(Meeting)

    class Arguments:
        id = graphene.ID(required=True)
        name = graphene.String()
        start_time = graphene.types.datetime.DateTime()
        end_time = graphene.types.datetime.DateTime()

    @staticmethod
    @has_meeting
    def mutate(root, info, **kwargs):
        meeting = info.context.meeting

        assign(kwargs, meeting, 'name')
        assign(kwargs, meeting, 'start_time')
        assign(kwargs, meeting, 'end_time')
        meeting.save()

        return UpdateMeeting(meeting=meeting)


class DeleteMeeting(graphene.Mutation):
    ok = graphene.Boolean()

    class Arguments:
        id = graphene.ID(required=True)

    @staticmethod
    @has_meeting
    def mutate(root, info, **kwargs):
        info.context.meeting.delete()
        return DeleteMeeting(ok=True)


class ProgramQuery(graphene.ObjectType):
    program = graphene.Field(Program, id=graphene.ID(required=True))
    meeting = graphene.Field(Meeting, id=graphene.ID(required=True))
    all_programs = DjangoFilterConnectionField(Program)
    all_meetings = DjangoFilterConnectionField(Meeting, program_id=graphene.ID())

    @staticmethod
    @has_program
    def resolve_program(root, info, **kwargs):
        return info.context.program

    @staticmethod
    @has_meeting
    def resolve_meeting(root, info, **kwargs):
        return info.context.meeting

    @staticmethod
    def resolve_all_meetings(root, info, **kwargs):
        meetings = models.Meeting.objects.all()

        program_id = kwargs.get('program_id')
        if program_id:
            program = get_object_from_global_id(models.Program, program_id)
            meetings = meetings.filter(program=program)

        return meetings


class ProgramMutation(graphene.ObjectType):
    create_program = CreateProgram.Field()
    update_program = UpdateProgram.Field()
    delete_program = DeleteProgram.Field()
    create_meeting = CreateMeeting.Field()
    update_meeting = UpdateMeeting.Field()
    delete_meeting = DeleteMeeting.Field()