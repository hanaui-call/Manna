import logging

from django_server.const import ProgramStateEnum, MannaError, ManClassEnum
from django_server.graphene.utils import get_global_id_from_object
from django_server.models import ProgramParticipant, MeetingParticipant
from django_server.test.test_base import BaseTestCase

logger = logging.getLogger(__name__)


class ParticipanceTestCase(BaseTestCase):
    def test_participate_program(self):
        program = self.create_program(name='프로그램1', description='프로그램1설명입니다.', user=self.user)

        gql = """
        mutation ParticipateProgram($programId:ID!) {
            participateProgram(programId:$programId) {
                programParticipant {
                    program {
                        name
                    }
                    participant {
                        name
                    }
                }
            }
        }
        """
        variables = {
            'programId': get_global_id_from_object('Program', program.pk),
        }

        data = self.execute(gql, variables, user=self.user)['participateProgram']['programParticipant']
        self.assertEqual(self.user.name, data['participant']['name'])
        self.assertEqual(program.name, data['program']['name'])

        user = self.create_user(username='second_user', email='second@dev.ai')
        data = self.execute(gql, variables, user=user)['participateProgram']['programParticipant']
        self.assertEqual(user.name, data['participant']['name'])
        self.assertEqual(program.name, data['program']['name'])

        self.assertEqual(2, ProgramParticipant.objects.filter(program=program).count())

    def test_participate_end_program(self):
        program = self.create_program(name='프로그램1', description='프로그램1설명입니다.', user=self.user,
                                      state=ProgramStateEnum.END.value)

        gql = """
        mutation ParticipateProgram($programId:ID!) {
            participateProgram(programId:$programId) {
                error {
                    key
                    message
                }
            }
        }
        """
        variables = {
            'programId': get_global_id_from_object('Program', program.pk),
        }

        data = self.execute(gql, variables, user=self.user)['participateProgram']['error']
        self.assertEqual(MannaError.EXPIRED.name, data['key'])
        self.assertEqual('the program is expired.', data['message'])

    def test_participate_meeting(self):
        program = self.create_program(name='프로그램1', description='프로그램1설명입니다.', user=self.user)
        meeting = self.create_meeting(name='미팅1', program=program)

        gql = """
        mutation ParticipateMeeting($meetingId:ID!) {
            participateMeeting(meetingId:$meetingId) {
                meetingParticipant {
                    meeting {
                        name
                    }
                    participant {
                        name
                    }
                }
            }
        }
        """
        variables = {
            'meetingId': get_global_id_from_object('Meeting', meeting.pk),
        }

        data = self.execute(gql, variables, user=self.user)['participateMeeting']['meetingParticipant']
        self.assertEqual(self.user.name, data['participant']['name'])
        self.assertEqual(meeting.name, data['meeting']['name'])

        user = self.create_user(username='second_user', email='second@dev.ai')
        data = self.execute(gql, variables, user=user)['participateMeeting']['meetingParticipant']
        self.assertEqual(user.name, data['participant']['name'])
        self.assertEqual(meeting.name, data['meeting']['name'])

        self.assertEqual(2, MeetingParticipant.objects.filter(meeting=meeting).count())

    def test_leave_program(self):
        program = self.create_program(name='프로그램1', description='프로그램1설명입니다.', user=self.user)
        user = self.create_user(username='second_user', email='second@dev.ai')

        ProgramParticipant.objects.create(program=program, participant=self.user)
        ProgramParticipant.objects.create(program=program, participant=user)

        gql = """
        mutation LeaveProgram($programId:ID!, $userId:ID!) {
            leaveProgram(programId:$programId, userId:$userId) {
                program {
                    name
                }
                error {
                    key
                }
            }
        }
        """
        variables = {
            'programId': get_global_id_from_object('Program', program.pk),
            'userId': get_global_id_from_object('Profile', user.pk),
        }

        self.assertEqual(2, ProgramParticipant.objects.filter(program=program).count())
        data = self.execute(gql, variables, user=self.user)['leaveProgram']['program']
        self.assertEqual(program.name, data['name'])
        self.assertEqual(1, ProgramParticipant.objects.filter(program=program).count())
        self.assertEqual(self.user.user.username,
                         ProgramParticipant.objects.filter(program=program).first().participant.user.username)

        ProgramParticipant.objects.create(program=program, participant=user)
        user2 = self.create_user(username='third_user', email='third@dev.ai')
        data = self.execute(gql, variables, user=user2)['leaveProgram']['error']
        self.assertEqual(MannaError.INVALID_PERMISSION.name, data['key'])
        self.assertEqual(2, ProgramParticipant.objects.filter(program=program).count())

        admin_user = self.create_user(username='admin_user', email='admin@dev.ai', role=ManClassEnum.ADMIN.value)
        variables = {
            'programId': get_global_id_from_object('Program', program.pk),
            'userId': get_global_id_from_object('Profile', user.pk),
        }
        data = self.execute(gql, variables, user=admin_user)['leaveProgram']['program']
        self.assertEqual(program.name, data['name'])
        self.assertEqual(1, ProgramParticipant.objects.filter(program=program).count())

    def test_leave_meeting(self):
        program = self.create_program(name='프로그램1', description='프로그램1설명입니다.', user=self.user)
        meeting = self.create_meeting(name='미팅1', program=program)
        user = self.create_user(username='second_user', email='second@dev.ai')

        MeetingParticipant.objects.create(meeting=meeting, participant=self.user)
        MeetingParticipant.objects.create(meeting=meeting, participant=user)

        gql = """
        mutation LeaveMeeting($meetingId:ID!) {
            leaveMeeting(meetingId:$meetingId) {
                meeting {
                    name
                }
            }
        }
        """
        variables = {
            'meetingId': get_global_id_from_object('Meeting', meeting.pk),
        }

        self.assertEqual(2, MeetingParticipant.objects.filter(meeting=meeting).count())
        data = self.execute(gql, variables, user=self.user)['leaveMeeting']['meeting']
        self.assertEqual(meeting.name, data['name'])
        self.assertEqual(1, MeetingParticipant.objects.filter(meeting=meeting).count())
        self.assertEqual(user.user.username,
                         MeetingParticipant.objects.filter(meeting=meeting).first().participant.user.username)
