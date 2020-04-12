import logging

import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField

from django_server import const
from django_server import models
from django_server.graphene.base import ManClass, ProgramState, Error
from django_server.graphene.utils import get_object_from_global_id, has_program, assign, has_meeting
from django_server.libs.authentification import authorization

logger = logging.getLogger(__name__)


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


class ProgramParicipant(DjangoObjectType):
    class Meta:
        model = models.ProgramParticipant
        interfaces = (graphene.Node,)


class MeetingParicipant(DjangoObjectType):
    class Meta:
        model = models.MeetingParticipant
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
    @authorization
    def mutate(root, info, **kwargs):
        name = kwargs.get('name')
        description = kwargs.get('description', '')
        space = get_object_from_global_id(models.Space, kwargs.get('space_id'))
        state = kwargs.get('state', const.ProgramStateEnum.INVITING.value)
        participants_min = kwargs.get('participants_min', 1)
        participants_max = kwargs.get('participants_max', 10)
        required_man_class = kwargs.get('required_man_class', const.ManClassEnum.NON_MEMBER.value)
        open_time = kwargs.get('open_time')
        close_time = kwargs.get('close_time')

        user = info.context.user

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
    @authorization
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
    @authorization
    @has_program
    def mutate(root, info, **kwargs):
        info.context.program.delete()
        return DeleteProgram(ok=True)


class CreateMeeting(graphene.Mutation):
    meeting = graphene.Field(Meeting)
    error = graphene.Field(Error)

    class Arguments:
        name = graphene.String(required=True)
        program_id = graphene.ID(required=True)
        space_id = graphene.ID()
        start_time = graphene.types.datetime.DateTime(required=True)
        end_time = graphene.types.datetime.DateTime(required=True)

    @staticmethod
    @authorization
    def mutate(root, info, **kwargs):
        name = kwargs.get('name')
        program = get_object_from_global_id(models.Program, kwargs.get('program_id'))
        space = get_object_from_global_id(models.Space, kwargs.get('space_id'))
        start_time = kwargs.get('start_time')
        end_time = kwargs.get('end_time')

        # check to duplicate reservations
        if space and models.Meeting.objects.filter(space=space,
                                                   start_time__lt=start_time,
                                                   end_time__gt=start_time).count() > 0:
            return CreateMeeting(error=Error(key=const.MannaError.DUPLICATED, message="duplicate time"))

        meeting = models.Meeting.objects.create(name=name,
                                                program=program,
                                                space=space,
                                                start_time=start_time,
                                                end_time=end_time)

        return CreateMeeting(meeting=meeting)


class UpdateMeeting(graphene.Mutation):
    meeting = graphene.Field(Meeting)
    error = graphene.Field(Error)

    class Arguments:
        id = graphene.ID(required=True)
        space_id = graphene.ID()
        name = graphene.String()
        start_time = graphene.types.datetime.DateTime()
        end_time = graphene.types.datetime.DateTime()

    @staticmethod
    @authorization
    @has_meeting
    def mutate(root, info, **kwargs):
        meeting = info.context.meeting

        assign(kwargs, meeting, 'name')
        assign(kwargs, meeting, 'start_time')
        assign(kwargs, meeting, 'end_time')

        space_id = kwargs.get('space_id')
        if space_id:
            space = get_object_from_global_id(models.Space, space_id)

            # check to duplicate reservations
            if models.Meeting.objects.filter(space=space,
                                             start_time__lt=meeting.start_time,
                                             end_time__gt=meeting.start_time).count() > 0:
                return UpdateMeeting(error=Error(key=const.MannaError.DUPLICATED, message="duplicate time"))
            meeting.space = space

        meeting.save()

        return UpdateMeeting(meeting=meeting)


class DeleteMeeting(graphene.Mutation):
    ok = graphene.Boolean()

    class Arguments:
        id = graphene.ID(required=True)

    @staticmethod
    @authorization
    @has_meeting
    def mutate(root, info, **kwargs):
        info.context.meeting.delete()
        return DeleteMeeting(ok=True)


class ParticipateProgram(graphene.Mutation):
    program_participant = graphene.Field(ProgramParicipant)
    error = graphene.Field(Error)

    class Arguments:
        program_id = graphene.ID(required=True)

    @staticmethod
    @authorization
    def mutate(root, info, **kwargs):
        user = info.context.user
        program = get_object_from_global_id(models.Program, kwargs.get('program_id'))

        if models.ProgramParticipant.objects.filter(program=program).count() >= program.participants_max:
            return ParticipateProgram(error=Error(key=const.MannaError.MAX_PARTICIPANT,
                                                  message="the participants have been exceeded."))

        program_participant = models.ProgramParticipant.objects.create(program=program, participant=user)

        return ParticipateProgram(program_participant=program_participant)


class LeaveProgram(graphene.Mutation):
    program = graphene.Field(Program)

    class Arguments:
        program_id = graphene.ID(required=True)

    @staticmethod
    @authorization
    def mutate(root, info, **kwargs):
        user = info.context.user
        program = get_object_from_global_id(models.Program, kwargs.get('program_id'))

        models.ProgramParticipant.objects.get(program=program, participant=user).delete()
        return LeaveProgram(program=program)


class LeaveMeeting(graphene.Mutation):
    meeting = graphene.Field(Meeting)

    class Arguments:
        meeting_id = graphene.ID(required=True)

    @staticmethod
    @authorization
    def mutate(root, info, **kwargs):
        user = info.context.user
        meeting = get_object_from_global_id(models.Meeting, kwargs.get('meeting_id'))

        models.MeetingParticipant.objects.get(meeting=meeting, participant=user).delete()
        return LeaveMeeting(meeting=meeting)


class ParticipateMeeting(graphene.Mutation):
    meeting_participant = graphene.Field(MeetingParicipant)
    error = graphene.Field(Error)

    class Arguments:
        meeting_id = graphene.ID(required=True)

    @staticmethod
    @authorization
    def mutate(root, info, **kwargs):
        user = info.context.user
        meeting = get_object_from_global_id(models.Meeting, kwargs.get('meeting_id'))

        if models.MeetingParticipant.objects.filter(meeting=meeting).count() >= meeting.program.participants_max:
            return ParticipateProgram(error=Error(key=const.MannaError.MAX_PARTICIPANT,
                                                  message="the participants have been exceeded."))

        meeting_participant = models.MeetingParticipant.objects.create(meeting=meeting, participant=user)

        return ParticipateMeeting(meeting_participant=meeting_participant)


class ProgramQuery(graphene.ObjectType):
    program = graphene.Field(Program, id=graphene.ID(required=True))
    meeting = graphene.Field(Meeting, id=graphene.ID(required=True))
    all_programs = DjangoFilterConnectionField(Program)
    all_meetings = DjangoFilterConnectionField(Meeting, program_id=graphene.ID())

    @staticmethod
    def resolve_program(root, info, **kwargs):
        program = get_object_from_global_id(models.Program, kwargs.get('id'))
        return program

    @staticmethod
    def resolve_meeting(root, info, **kwargs):
        meeting = get_object_from_global_id(models.Meeting, kwargs.get('id'))
        return meeting

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

    participate_program = ParticipateProgram.Field()
    leave_program = LeaveProgram.Field()
    participate_meeting = ParticipateMeeting.Field()
    leave_meeting = LeaveMeeting.Field()
