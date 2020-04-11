import logging
from datetime import datetime

from django_server.const import ProgramStateEnum, ManClassEnum, MannaError
from django_server.graphene.utils import get_global_id_from_object
from django_server.models import Program, Meeting, ProgramParticipant, MeetingParticipant
from django_server.test.test_base import BaseTestCase

logger = logging.getLogger(__name__)


class SpaceTestCase(BaseTestCase):
    def test_create_program(self):
        space_name = '장소1'
        space = self.create_space(space_name, user=self.user)

        gql = """
        mutation CreateProgram($name:String!, $description:String, $state:ProgramStateEnum, $openTime:DateTime!, $spaceId:ID) {
            createProgram(name:$name, description:$description, state:$state, openTime:$openTime, spaceId:$spaceId) {
                program {
                    name
                    description
                    state
                    openTime
                    space {
                        name
                    }
                }
            }
        }
        """
        variables = {
            'name': '프로그램1',
            'description': '프로그램1 입니다.',
            'state': ProgramStateEnum.INVITING.name,
            'openTime': '2020-02-14T20:10:00+09:00',
            'spaceId': get_global_id_from_object('Space', space.pk)
        }

        data = self.execute(gql, variables, user=self.user)['createProgram']['program']
        self.assertEqual(variables['name'], data['name'])
        self.assertEqual(variables['description'], data['description'])
        self.assertEqual(variables['state'], data['state'])
        self.assertEqual(variables['openTime'], data['openTime'])
        self.assertEqual(space_name, data['space']['name'])
        self.assertEqual(1, Program.objects.all().count())

    def test_update_program(self):
        program = self.create_program(name='프로그램1', description='프로그램1설명입니다.', user=self.user)

        gql = """
        mutation UpdateProgram($id:ID!, $name:String!, $description:String, $requiredManClass:ManClassEnum $openTime:DateTime!, $closeTime:DateTime) {
            updateProgram(id:$id, name:$name, description:$description, requiredManClass:$requiredManClass, openTime:$openTime, closeTime:$closeTime) {
                program {
                    name
                    description
                    requiredManClass
                    openTime
                    closeTime
                }
            }
        }
        """
        variables = {
            'id': get_global_id_from_object('Program', program.pk),
            'name': '프로그램1',
            'description': '프로그램1 입니다.',
            'requiredManClass': ManClassEnum.GUEST.name,
            'openTime': '2020-02-14T20:10:00+09:00',
            'closeTime': '2020-02-22T20:30:00+09:00',
        }

        data = self.execute(gql, variables, user=self.user)['updateProgram']['program']
        self.assertEqual(variables['name'], data['name'])
        self.assertEqual(variables['description'], data['description'])
        self.assertEqual(variables['requiredManClass'], data['requiredManClass'])
        self.assertEqual(variables['openTime'], data['openTime'])
        self.assertEqual(variables['closeTime'], data['closeTime'])

    def test_delete_program(self):
        program = self.create_program(name='프로그램1', description='프로그램1설명입니다.', user=self.user)

        gql = """
        mutation DeleteProgram($id:ID!) {
            deleteProgram(id:$id) {
                ok
            }
        }
        """
        variables = {
            'id': get_global_id_from_object('Program', program.pk),
        }

        self.assertEqual(1, Program.objects.all().count())

        ok = self.execute(gql, variables, user=self.user)['deleteProgram']['ok']
        self.assertTrue(ok)

        self.assertEqual(0, Program.objects.all().count())

    def test_create_meeting(self):
        program_name = '프로그램1'
        program = self.create_program(name=program_name, description='프로그램1설명입니다.', user=self.user)

        gql = """
        mutation CreateMeeting($name:String!, $programId:ID!, $startTime:DateTime!, $endTime:DateTime!, $spaceId:ID) {
            createMeeting(name:$name, startTime:$startTime, endTime:$endTime, programId:$programId, spaceId:$spaceId) {
                meeting {
                    name
                    startTime
                    endTime
                    program {
                        name
                    }
                    space {
                        name
                    }
                }
            }
        }
        """
        variables = {
            'name': 'meet1',
            'startTime': '2020-02-14T20:10:00+09:00',
            'endTime': '2020-02-14T21:10:00+09:00',
            'programId': get_global_id_from_object('Program', program.pk),
            'spaceId': get_global_id_from_object('Space', program.space.pk)
        }

        data = self.execute(gql, variables, user=self.user)['createMeeting']['meeting']
        self.assertEqual(variables['name'], data['name'])
        self.assertEqual(variables['startTime'], data['startTime'])
        self.assertEqual(variables['endTime'], data['endTime'])
        self.assertEqual(program_name, data['program']['name'])
        self.assertEqual(program.space.name, data['space']['name'])
        self.assertEqual(1, Program.objects.all().count())

    def test_update_meeting(self):
        program = self.create_program(name='프로그램1', description='프로그램1설명입니다.', user=self.user)
        meeting = self.create_meeting(name='미팅1', program=program)

        gql = """
        mutation UpdateMeeting($id:ID!, $name:String, $startTime:DateTime, $endTime:DateTime, $spaceId:ID) {
            updateMeeting(id:$id, name:$name, startTime:$startTime, endTime:$endTime, spaceId:$spaceId ) {
                meeting {
                    name
                    startTime
                    endTime
                    space {
                        name
                    }
                }
            }
        }
        """
        variables = {
            'name': 'meet1',
            'startTime': '2020-02-14T20:10:00+09:00',
            'endTime': '2020-02-14T21:10:00+09:00',
            'id': get_global_id_from_object('Meeting', meeting.pk),
            'spaceId': get_global_id_from_object('Space', program.space.pk)
        }

        data = self.execute(gql, variables, user=self.user)['updateMeeting']['meeting']
        self.assertEqual(variables['name'], data['name'])
        self.assertEqual(variables['startTime'], data['startTime'])
        self.assertEqual(variables['endTime'], data['endTime'])
        self.assertEqual(program.space.name, data['space']['name'])

    def test_delete_meeting(self):
        program = self.create_program(name='프로그램1', description='프로그램1설명입니다.', user=self.user)
        meeting1 = self.create_meeting(name='미팅1', program=program)
        self.create_meeting(name='미팅2', program=program)

        gql = """
        mutation DeleteMeeting($id:ID!) {
            deleteMeeting(id:$id) {
                ok
            }
        }
        """
        variables = {
            'id': get_global_id_from_object('Meeting', meeting1.pk),
        }

        self.assertEqual(2, Meeting.objects.all().count())

        ok = self.execute(gql, variables, user=self.user)['deleteMeeting']['ok']
        self.assertTrue(ok)

        self.assertEqual(1, Meeting.objects.all().count())

    def test_check_for_duplicate_reservations(self):
        program = self.create_program(name='프로그램1', description='프로그램1설명입니다.', user=self.user)
        self.create_meeting(name='미팅1',
                            program=program,
                            start_time=datetime(2020, 3, 1, 12, 0),
                            end_time=datetime(2020, 3, 1, 13, 0))

        # create
        gql = """
        mutation CreateMeeting($name:String!, $programId:ID!, $startTime:DateTime!, $endTime:DateTime!, $spaceId:ID) {
            createMeeting(name:$name, startTime:$startTime, endTime:$endTime, programId:$programId, spaceId:$spaceId) {
                meeting {
                    id
                    name
                    startTime
                    endTime
                    program {
                        name
                    }
                    space {
                        name
                    }
                }
                error {
                    key
                    message
                }
            }
        }
        """
        variables = {
            'name': 'meet1',
            'startTime': '2020-03-01T12:30:00+09:00',
            'endTime': '2020-03-01T13:30:00+09:00',
            'programId': get_global_id_from_object('Program', program.pk),
            'spaceId': get_global_id_from_object('Space', program.space.pk)
        }

        data = self.execute(gql, variables, user=self.user)['createMeeting']
        self.assertEqual(MannaError.DUPLICATED.name, data['error']['key'])
        self.assertIsNone(data['meeting'])

        variables = {
            'name': 'meet1',
            'startTime': '2020-03-01T13:00:00+09:00',
            'endTime': '2020-03-01T14:00:00+09:00',
            'programId': get_global_id_from_object('Program', program.pk),
            'spaceId': get_global_id_from_object('Space', program.space.pk)
        }

        data = self.execute(gql, variables, user=self.user)['createMeeting']
        self.assertIsNone(data['error'])
        self.assertEqual(variables['name'], data['meeting']['name'])
        self.assertEqual(2, Meeting.objects.all().count())

        meeting_id = data['meeting']['id']

        # update
        gql = """
        mutation UpdateMeeting($id:ID!, $name:String, $startTime:DateTime, $endTime:DateTime, $spaceId:ID) {
            updateMeeting(id:$id, name:$name, startTime:$startTime, endTime:$endTime, spaceId:$spaceId ) {
                meeting {
                    name
                    startTime
                    endTime
                    space {
                        name
                    }
                }
                error {
                    key
                    message
                }
            }
        }
        """
        variables = {
            'name': 'meet1',
            'startTime': '2020-03-01T13:30:00+09:00',
            'endTime': '2020-03-01T14:30:00+09:00',
            'id': meeting_id,
            'spaceId': get_global_id_from_object('Space', program.space.pk)
        }

        data = self.execute(gql, variables, user=self.user)['updateMeeting']
        self.assertEqual(MannaError.DUPLICATED.name, data['error']['key'])
        self.assertIsNone(data['meeting'])

        variables = {
            'name': 'meet1',
            'startTime': '2020-03-01T14:00:00+09:00',
            'endTime': '2020-03-01T15:00:00+09:00',
            'id': meeting_id,
            'spaceId': get_global_id_from_object('Space', program.space.pk)
        }

        data = self.execute(gql, variables, user=self.user)['updateMeeting']
        self.assertIsNone(data['error'])
        self.assertEqual(variables['name'], data['meeting']['name'])
        self.assertEqual(2, Meeting.objects.all().count())

    def test_program_participant(self):
        program = self.create_program(name='프로그램1', description='프로그램1설명입니다.', user=self.user, participants_max=4)
        user1 = self.create_user('user1', 'user1@test.ai', 'user1', 'password')
        user2 = self.create_user('user2', 'user2@test.ai', 'user2', 'password')
        user3 = self.create_user('user3', 'user3@test.ai', 'user3', 'password')
        user4 = self.create_user('user4', 'user4@test.ai', 'user4', 'password')
        user5 = self.create_user('user5', 'user5@test.ai', 'user5', 'password')

        ProgramParticipant.objects.create(program=program, participant=user1)
        ProgramParticipant.objects.create(program=program, participant=user2)
        ProgramParticipant.objects.create(program=program, participant=user3)

        gql = """
        mutation ParticipateProgram($programId:ID!) {
            participateProgram(programId:$programId) {
                programParticipant {
                    program {
                        name
                    }
                    participant {
                        nickname
                    }
                }
                error {
                    key
                    message
                }
            }
        }
        """
        variables = {
            'programId': get_global_id_from_object('Program', program.pk)
        }

        data = self.execute(gql, variables, user=user4)['participateProgram']
        self.assertEqual(program.name, data['programParticipant']['program']['name'])
        self.assertEqual(user4.nickname, data['programParticipant']['participant']['nickname'])
        self.assertIsNone(data['error'])
        self.assertEqual(4, ProgramParticipant.objects.all().count())

        data = self.execute(gql, variables, user=user5)['participateProgram']
        self.assertEqual(MannaError.MAX_PARTICIPANT.name, data['error']['key'])
        self.assertEqual(4, ProgramParticipant.objects.all().count())

        gql = """
        mutation LeaveProgram($programId:ID!){
            leaveProgram(programId:$programId) {
                program {
                    name
                }
            }
        }
        """
        variables = {
            'programId': get_global_id_from_object('Program', program.pk)
        }
        self.execute(gql, variables, user=user1)
        self.assertEqual(3, ProgramParticipant.objects.all().count())

    def test_meeting_participant(self):
        program = self.create_program(name='프로그램1', description='프로그램1설명입니다.', user=self.user, participants_max=4)
        meeting = self.create_meeting(name='미팅1', program=program)
        user1 = self.create_user('user1', 'user1@test.ai', 'user1', 'password')
        user2 = self.create_user('user2', 'user2@test.ai', 'user2', 'password')
        user3 = self.create_user('user3', 'user3@test.ai', 'user3', 'password')
        user4 = self.create_user('user4', 'user4@test.ai', 'user4', 'password')
        user5 = self.create_user('user5', 'user5@test.ai', 'user5', 'password')

        MeetingParticipant.objects.create(meeting=meeting, participant=user1)
        MeetingParticipant.objects.create(meeting=meeting, participant=user2)
        MeetingParticipant.objects.create(meeting=meeting, participant=user3)

        gql = """
        mutation ParticipateMeeting($meetingId:ID!) {
            participateMeeting(meetingId:$meetingId) {
                meetingParticipant {
                    meeting {
                        name
                    }
                    participant {
                        nickname
                    }
                }
                error {
                    key
                    message
                }
            }
        }
        """
        variables = {
            'meetingId': get_global_id_from_object('Meeting', meeting.pk)
        }

        data = self.execute(gql, variables, user=user4)['participateMeeting']
        self.assertEqual(meeting.name, data['meetingParticipant']['meeting']['name'])
        self.assertEqual(user4.nickname, data['meetingParticipant']['participant']['nickname'])
        self.assertIsNone(data['error'])
        self.assertEqual(4, MeetingParticipant.objects.all().count())

        data = self.execute(gql, variables, user=user5)['participateMeeting']
        self.assertEqual(MannaError.MAX_PARTICIPANT.name, data['error']['key'])
        self.assertEqual(4, MeetingParticipant.objects.all().count())

        gql = """
        mutation LeaveMeeting($meetingId:ID!){
            leaveMeeting(meetingId:$meetingId) {
                meeting {
                    name
                }
            }
        }
        """
        variables = {
            'meetingId': get_global_id_from_object('Meeting', meeting.pk)
        }
        self.execute(gql, variables, user=user1)
        self.assertEqual(3, MeetingParticipant.objects.all().count())
