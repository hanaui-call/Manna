import calendar
import datetime
import logging

import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField

from django_server import const
from django_server import models
from django_server.graphene.base import (ManClass, ProgramState, Error, ProgramTagType,
                                         Program, Meeting, is_editable_program)
from django_server.graphene.utils import get_object_from_global_id, has_program, assign, has_meeting
from django_server.libs.authentification import authorization

logger = logging.getLogger(__name__)


def is_duplicated_space(space, start_time, end_time, meeting=None):
    meetings = models.Meeting.objects.all()
    if meeting:
        meetings = meetings.exclude(id=meeting.id)

    if meetings.filter(space=space, start_time__lte=start_time, end_time__gt=start_time).count() > 0:
        return True
    if meetings.filter(space=space, start_time__lt=end_time, end_time__gte=end_time).count() > 0:
        return True
    return False


def is_duplicated_zoom(zoom, start_time, end_time, meeting=None):
    meetings = models.Meeting.objects.all()
    if meeting:
        meetings = meetings.exclude(id=meeting.id)

    if meetings.filter(zoom=zoom, start_time__lte=start_time, end_time__gt=start_time).count() > 0:
        return True
    if meetings.filter(zoom=zoom, start_time__lt=end_time, end_time__gte=end_time).count() > 0:
        return True
    return False


def get_duplicate_idx(lst):
    for i, argument in enumerate(lst):
        meeting = None
        if hasattr(argument, 'id'):
            meeting = get_object_from_global_id(models.Meeting, argument.id)

        space = get_object_from_global_id(models.Space, argument.space_id)
        zoom = get_object_from_global_id(models.Zoom, argument.zoom_id)
        start_time = argument.start_time
        end_time = argument.end_time

        if space and is_duplicated_space(space, start_time, end_time, meeting):
            return True, i
        if zoom and is_duplicated_zoom(zoom, start_time, end_time, meeting):
            return True, i

    return False, -1


class MeetingInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    program_id = graphene.ID(required=True)
    space_id = graphene.ID()
    zoom_id = graphene.ID()
    start_time = graphene.types.datetime.DateTime(required=True)
    end_time = graphene.types.datetime.DateTime(required=True)


class MeetingUpdateInput(graphene.InputObjectType):
    id = graphene.ID(required=True)
    space_id = graphene.ID()
    zoom_id = graphene.ID()
    name = graphene.String()
    start_time = graphene.types.datetime.DateTime()
    end_time = graphene.types.datetime.DateTime()


class ProgramTag(DjangoObjectType):
    type = graphene.Field(ProgramTagType)

    class Meta:
        model = models.ProgramTag
        interfaces = (graphene.Node,)

    @staticmethod
    def resolve_type(root, info, **kwargs):
        return root.type


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
        tag_id = graphene.ID(required=True)

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
        tag = get_object_from_global_id(models.ProgramTag, kwargs.get('tag_id'))

        user = info.context.user

        program = models.Program.objects.create(name=name,
                                                description=description,
                                                space=space,
                                                state=state,
                                                participants_max=participants_max,
                                                participants_min=participants_min,
                                                required_man_class=required_man_class,
                                                tag=tag,
                                                owner=user)

        models.ProgramParticipant.objects.create(program=program, participant=user)

        return CreateProgram(program=program)


class UpdateProgram(graphene.Mutation):
    program = graphene.Field(Program)
    error = graphene.Field(Error)

    class Arguments:
        id = graphene.ID(required=True)
        name = graphene.String()
        description = graphene.String()
        space_id = graphene.ID()
        state = graphene.Argument(ProgramState)
        participants_min = graphene.Int()
        participants_max = graphene.Int()
        required_man_class = graphene.Argument(ManClass)
        tag_id = graphene.ID()

    @staticmethod
    @authorization
    @has_program
    def mutate(root, info, **kwargs):
        if not is_editable_program(info.context.program, info.context.user):
            return DeleteProgram(error=Error(key=const.MannaError.INVALID_PERMISSION, message="invalid permission"))

        program = info.context.program

        assign(kwargs, program, 'name')
        assign(kwargs, program, 'description')
        assign(kwargs, program, 'state')
        assign(kwargs, program, 'participants_min')
        assign(kwargs, program, 'participants_max')
        assign(kwargs, program, 'required_man_class')

        space_id = kwargs.get('space_id')
        if space_id:
            space = get_object_from_global_id(models.Space, space_id)
            program.space = space

        tag_id = kwargs.get('tag_id')
        if tag_id:
            tag = get_object_from_global_id(models.ProgramTag, tag_id)
            program.tag = tag

        program.save()

        return UpdateProgram(program=program)


class DeleteProgram(graphene.Mutation):
    ok = graphene.Boolean()
    error = graphene.Field(Error)

    class Arguments:
        id = graphene.ID(required=True)

    @staticmethod
    @authorization
    @has_program
    def mutate(root, info, **kwargs):
        if not is_editable_program(info.context.program, info.context.user):
            return DeleteProgram(error=Error(key=const.MannaError.INVALID_PERMISSION, message="invalid permission"))

        info.context.program.delete()
        return DeleteProgram(ok=True)


class CreateMeeting(graphene.Mutation):
    meeting = graphene.Field(Meeting)
    error = graphene.Field(Error)

    class Arguments:
        argument = graphene.Argument(MeetingInput, required=True)

    @staticmethod
    @authorization
    def mutate(root, info, **kwargs):
        argument = kwargs.get('argument')
        name = argument.name
        program = get_object_from_global_id(models.Program, argument.program_id)
        space = get_object_from_global_id(models.Space, argument.space_id)
        zoom = get_object_from_global_id(models.Zoom, argument.zoom_id)
        start_time = argument.start_time
        end_time = argument.end_time

        # check to duplicate reservations
        if space and is_duplicated_space(space, start_time, end_time):
            return CreateMeeting(error=Error(key=const.MannaError.DUPLICATED, message="space duplicate time"))
        if zoom and is_duplicated_zoom(zoom, start_time, end_time):
            return CreateMeeting(error=Error(key=const.MannaError.ZOOM_DUPLICATED, message="zoom duplicate time"))

        if start_time > end_time:
            return CreateMeeting(error=Error(key=const.MannaError.INVALID_TIME, message="invalid time"))

        meeting = models.Meeting.objects.create(name=name,
                                                program=program,
                                                space=space,
                                                zoom=zoom,
                                                start_time=start_time,
                                                end_time=end_time)

        return CreateMeeting(meeting=meeting)


class UpdateMeeting(graphene.Mutation):
    meeting = graphene.Field(Meeting)
    error = graphene.Field(Error)

    class Arguments:
        id = graphene.ID(required=True)
        space_id = graphene.ID()
        zoom_id = graphene.ID()
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
            if is_duplicated_space(space, meeting.start_time, meeting.end_time):
                return UpdateMeeting(error=Error(key=const.MannaError.DUPLICATED, message="space duplicate time"))
            meeting.space = space

        zoom_id = kwargs.get('zoom_id')
        if zoom_id:
            zoom = get_object_from_global_id(models.Zoom, zoom_id)

            # check to duplicate reservations
            if is_duplicated_zoom(zoom, meeting.start_time, meeting.end_time):
                return UpdateMeeting(error=Error(key=const.MannaError.ZOOM_DUPLICATED, message="zoom duplicate time"))
            meeting.zoom = zoom

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


class CreateMeetings(graphene.Mutation):
    meetings = graphene.List(Meeting)
    error_idx = graphene.Int()

    class Arguments:
        argument = graphene.Argument(graphene.List(MeetingInput), required=True)

    @staticmethod
    @authorization
    def mutate(root, info, **kwargs):
        ok, i = get_duplicate_idx(kwargs.get('argument'))
        if ok:
            return CreateMeetings(error_idx=i)

        meetings = []
        for argument in kwargs.get('argument'):
            name = argument.name
            program = get_object_from_global_id(models.Program, argument.program_id)
            space = get_object_from_global_id(models.Space, argument.space_id)
            zoom = get_object_from_global_id(models.Zoom, argument.zoom_id)
            start_time = argument.start_time
            end_time = argument.end_time

            meetings.append(models.Meeting.objects.create(name=name, program=program, space=space, zoom=zoom,
                                                          start_time=start_time, end_time=end_time))
        return CreateMeetings(meetings=meetings, error_idx=-1)


class UpdateMeetings(graphene.Mutation):
    meetings = graphene.List(Meeting)
    error_idx = graphene.Int()

    class Arguments:
        argument = graphene.Argument(graphene.List(MeetingUpdateInput), required=True)

    @staticmethod
    @authorization
    def mutate(root, info, **kwargs):
        # 나는 빼야함.
        ok, i = get_duplicate_idx(kwargs.get('argument'))
        if ok:
            return UpdateMeetings(error_idx=i)

        meetings = []
        for argument in kwargs.get('argument'):
            meeting = get_object_from_global_id(models.Meeting, argument.id)
            meeting.name = argument.name
            meeting.start_time = argument.start_time
            meeting.end_time = argument.end_time

            meeting.space = get_object_from_global_id(models.Space, argument.space_id)
            meeting.zoom = get_object_from_global_id(models.Zoom, argument.zoom_id)

            meeting.save()
            meetings.append(meeting)

        return UpdateMeetings(meetings=meetings, error_idx=-1)


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

        if program.state in [const.ProgramStateEnum.END.value, const.ProgramStateEnum.SUSPEND.value]:
            return ParticipateProgram(error=Error(key=const.MannaError.EXPIRED,
                                                  message="the program is expired."))

        if models.ProgramParticipant.objects.filter(program=program).count() >= program.participants_max:
            return ParticipateProgram(error=Error(key=const.MannaError.MAX_PARTICIPANT,
                                                  message="the participants have been exceeded."))

        program_participant = models.ProgramParticipant.objects.create(program=program, participant=user)

        return ParticipateProgram(program_participant=program_participant)


class LeaveProgram(graphene.Mutation):
    program = graphene.Field(Program)
    error = graphene.Field(Error)

    class Arguments:
        program_id = graphene.ID(required=True)
        user_id = graphene.ID(required=True)

    @staticmethod
    @authorization
    def mutate(root, info, **kwargs):
        user = info.context.user
        program = get_object_from_global_id(models.Program, kwargs.get('program_id'))
        target_user = get_object_from_global_id(models.Profile, kwargs.get('user_id'))

        if user == program.owner or user.role == const.ManClassEnum.ADMIN.value or user == target_user:
            models.ProgramParticipant.objects.get(program=program, participant=target_user).delete()
            return LeaveProgram(program=program)

        return LeaveProgram(error=Error(key=const.MannaError.INVALID_PERMISSION, message="Invalid permission"))


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
    program_tags = graphene.List(ProgramTag)
    zooms = graphene.Field(graphene.List(Meeting),
                           year=graphene.Int(required=True),
                           month=graphene.Int(required=True),
                           day=graphene.Int())

    @staticmethod
    def resolve_program(root, info, **kwargs):
        program = get_object_from_global_id(models.Program, kwargs.get('id'))
        return program

    @staticmethod
    def resolve_meeting(root, info, **kwargs):
        meeting = get_object_from_global_id(models.Meeting, kwargs.get('id'))
        return meeting

    @staticmethod
    def resolve_all_programs(root, info, **kwargs):
        return models.Program.objects.filter(state=const.ProgramStateEnum.PROGRESS.value)

    @staticmethod
    def resolve_all_meetings(root, info, **kwargs):
        meetings = models.Meeting.objects.all()

        program_id = kwargs.get('program_id')
        if program_id:
            program = get_object_from_global_id(models.Program, program_id)
            meetings = meetings.filter(program=program)

        return meetings

    @staticmethod
    @authorization
    def resolve_program_tags(root, info, **kwargs):
        return models.ProgramTag.objects.filter(is_active=True)

    @staticmethod
    @authorization
    def resolve_zooms(root, info, **kwargs):
        year = kwargs.get('year')
        month = kwargs.get('month')
        day = kwargs.get('day')

        if day:
            start_day = day
            last_day = day + 1
        else:
            start_day = 1
            last_day = calendar.monthrange(year, month)[1]

        start_date = datetime.date(year, month, start_day)
        end_date = datetime.date(year, month, last_day)

        return models.Meeting.objects.filter(zoom__isnull=False,
                                             start_time__range=(start_date, end_date))


class ProgramMutation(graphene.ObjectType):
    create_program = CreateProgram.Field()
    update_program = UpdateProgram.Field()
    delete_program = DeleteProgram.Field()
    create_meeting = CreateMeeting.Field()
    create_meetings = CreateMeetings.Field()
    update_meeting = UpdateMeeting.Field()
    update_meetings = UpdateMeetings.Field()
    delete_meeting = DeleteMeeting.Field()

    participate_program = ParticipateProgram.Field()
    leave_program = LeaveProgram.Field()
    participate_meeting = ParticipateMeeting.Field()
    leave_meeting = LeaveMeeting.Field()
