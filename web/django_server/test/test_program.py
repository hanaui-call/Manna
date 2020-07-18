import logging
from datetime import datetime

from django_server.const import ProgramStateEnum, ManClassEnum, MannaError, ProgramTagTypeEnum
from django_server.graphene.utils import get_global_id_from_object
from django_server.models import Program, Meeting, ProgramParticipant, MeetingParticipant, ProgramTag
from django_server.test.test_base import BaseTestCase

logger = logging.getLogger(__name__)


class SpaceTestCase(BaseTestCase):
    def test_create_program(self):
        space_name = '장소1'
        space = self.create_space(space_name, user=self.user)
        tag = ProgramTag.objects.first()

        gql = """
        mutation CreateProgram($name:String!, $description:String, $state:ProgramStateEnum, $spaceId:ID, $tagId:ID!) {
            createProgram(name:$name, description:$description, state:$state, spaceId:$spaceId, tagId:$tagId) {
                program {
                    name
                    description
                    state
                    space {
                        name
                    }
                    tag {
                        tag
                        type
                    }
                }
            }
        }
        """
        variables = {
            'name': '프로그램1',
            'description': '프로그램1 입니다.',
            'state': ProgramStateEnum.INVITING.name,
            'spaceId': get_global_id_from_object('Space', space.pk),
            'tagId': get_global_id_from_object('ProgramTag', tag.pk)
        }

        data = self.execute(gql, variables, user=self.user)['createProgram']['program']
        self.assertEqual(variables['name'], data['name'])
        self.assertEqual(variables['description'], data['description'])
        self.assertEqual(variables['state'], data['state'])
        self.assertEqual(space_name, data['space']['name'])
        self.assertEqual(tag.tag, data['tag']['tag'])
        self.assertEqual(1, Program.objects.all().count())

    def test_update_program(self):
        program = self.create_program(name='프로그램1', description='프로그램1설명입니다.', user=self.user)
        tag = ProgramTag.objects.last()
        member = self.create_user('user2', 'user2@test.ai', 'password')
        admin = self.create_user('user3', 'user3@test.ai', 'password', ManClassEnum.ADMIN.value)

        gql = """
        mutation UpdateProgram($id:ID!, $name:String!, $description:String, $requiredManClass:ManClassEnum, $tagId:ID) {
            updateProgram(id:$id, name:$name, description:$description, requiredManClass:$requiredManClass, tagId:$tagId) {
                program {
                    name
                    description
                    requiredManClass
                    tag {
                        tag
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
            'id': get_global_id_from_object('Program', program.pk),
            'name': '프로그램1',
            'description': '프로그램1 입니다.',
            'requiredManClass': ManClassEnum.GUEST.name,
            'tagId': get_global_id_from_object('ProgramTag', tag.pk)
        }

        data = self.execute(gql, variables, user=self.user)['updateProgram']['program']
        self.assertEqual(variables['name'], data['name'])
        self.assertEqual(variables['description'], data['description'])
        self.assertEqual(variables['requiredManClass'], data['requiredManClass'])
        self.assertEqual(tag.tag, data['tag']['tag'])

        data = self.execute(gql, variables, user=member)['updateProgram']
        self.assertEqual(MannaError.INVALID_PERMISSION.name, data['error']['key'])

        variables = {
            'id': get_global_id_from_object('Program', program.pk),
            'name': '프로그램1(admin)',
            'description': '프로그램1(admin) 입니다.',
        }
        data = self.execute(gql, variables, user=admin)['updateProgram']['program']
        self.assertEqual(variables['name'], data['name'])
        self.assertEqual(variables['description'], data['description'])

    def test_delete_program(self):
        program = self.create_program(name='프로그램1', description='프로그램1설명입니다.', user=self.user)
        member = self.create_user('user2', 'user2@test.ai', 'password')

        gql = """
        mutation DeleteProgram($id:ID!) {
            deleteProgram(id:$id) {
                ok
                error {
                    key
                    message
                }
            }
        }
        """
        variables = {
            'id': get_global_id_from_object('Program', program.pk),
        }
        data = self.execute(gql, variables, user=member)['deleteProgram']
        self.assertEqual(MannaError.INVALID_PERMISSION.name, data['error']['key'])

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

    def test_check_for_duplicate_zoom_reservations(self):
        program = self.create_program(name='프로그램1', description='프로그램1설명입니다.', user=self.user)
        zoom1 = self.create_zoom("Zoom1", 'zoom1@hanaui.net', 'hanaui', '123 456 7890', '1Nt', 'https://us04web.zoom.us/j/1')
        zoom2 = self.create_zoom("Zoom2", 'zoom2@hanaui.net', 'hanaui', '123 456 7899', '2Nt', 'https://us04web.zoom.us/j/2')

        self.create_meeting(name='미팅1',
                            program=program,
                            zoom=zoom1,
                            start_time=datetime(2020, 3, 1, 12, 0),
                            end_time=datetime(2020, 3, 1, 13, 0))

        # create
        gql = """
        mutation CreateMeeting($name:String!, $programId:ID!, $startTime:DateTime!, $endTime:DateTime!, $zoomId:ID) {
            createMeeting(name:$name, startTime:$startTime, endTime:$endTime, programId:$programId, zoomId:$zoomId) {
                meeting {
                    id
                    name
                    startTime
                    endTime
                    program {
                        name
                    }
                    zoom {
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
            'zoomId': get_global_id_from_object('Zoom', zoom1.pk)
        }

        data = self.execute(gql, variables, user=self.user)['createMeeting']
        self.assertEqual(MannaError.ZOOM_DUPLICATED.name, data['error']['key'])
        self.assertIsNone(data['meeting'])

        variables = {
            'name': 'meet1',
            'startTime': '2020-03-01T12:30:00+09:00',
            'endTime': '2020-03-01T13:30:00+09:00',
            'programId': get_global_id_from_object('Program', program.pk),
            'zoomId': get_global_id_from_object('Zoom', zoom2.pk)
        }

        data = self.execute(gql, variables, user=self.user)['createMeeting']
        self.assertIsNone(data['error'])
        self.assertEqual(variables['name'], data['meeting']['name'])
        self.assertEqual(2, Meeting.objects.all().count())

        meeting_id = data['meeting']['id']

        # update
        gql = """
        mutation UpdateMeeting($id:ID!, $name:String, $startTime:DateTime, $endTime:DateTime, $zoomId:ID) {
            updateMeeting(id:$id, name:$name, startTime:$startTime, endTime:$endTime, zoomId:$zoomId ) {
                meeting {
                    name
                    startTime
                    endTime
                    zoom {
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
            'endTime': '2020-03-01T14:30:00+09:00',
            'id': meeting_id,
            'zoomId': get_global_id_from_object('Zoom', zoom1.pk)
        }

        data = self.execute(gql, variables, user=self.user)['updateMeeting']
        self.assertEqual(MannaError.ZOOM_DUPLICATED.name, data['error']['key'])
        self.assertIsNone(data['meeting'])

        variables = {
            'name': 'meet1',
            'startTime': '2020-03-01T13:00:00+09:00',
            'endTime': '2020-03-01T15:00:00+09:00',
            'id': meeting_id,
            'zoomId': get_global_id_from_object('Zoom', zoom1.pk)
        }

        data = self.execute(gql, variables, user=self.user)['updateMeeting']
        self.assertIsNone(data['error'])
        self.assertEqual(variables['name'], data['meeting']['name'])
        self.assertEqual('Zoom1', data['meeting']['zoom']['name'])

    def test_program_participant(self):
        program = self.create_program(name='프로그램1', description='프로그램1설명입니다.', user=self.user, participants_max=4)
        user1 = self.create_user('user1', 'user1@test.ai', 'password')
        user2 = self.create_user('user2', 'user2@test.ai', 'password')
        user3 = self.create_user('user3', 'user3@test.ai', 'password')
        user4 = self.create_user('user4', 'user4@test.ai', 'password')
        user5 = self.create_user('user5', 'user5@test.ai', 'password')

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
            'programId': get_global_id_from_object('Program', program.pk)
        }

        data = self.execute(gql, variables, user=user4)['participateProgram']
        self.assertEqual(program.name, data['programParticipant']['program']['name'])
        self.assertEqual(user4.name, data['programParticipant']['participant']['name'])
        self.assertIsNone(data['error'])
        self.assertEqual(4, ProgramParticipant.objects.all().count())

        data = self.execute(gql, variables, user=user5)['participateProgram']
        self.assertEqual(MannaError.MAX_PARTICIPANT.name, data['error']['key'])
        self.assertEqual(4, ProgramParticipant.objects.all().count())

        gql = """
        mutation LeaveProgram($programId:ID!, $userId:ID!){
            leaveProgram(programId:$programId, userId:$userId) {
                program {
                    name
                }
            }
        }
        """
        variables = {
            'programId': get_global_id_from_object('Program', program.pk),
            'userId': get_global_id_from_object('Profile', user1.pk)
        }
        self.execute(gql, variables, user=user1)
        self.assertEqual(3, ProgramParticipant.objects.all().count())

    def test_meeting_participant(self):
        program = self.create_program(name='프로그램1', description='프로그램1설명입니다.', user=self.user, participants_max=4)
        meeting = self.create_meeting(name='미팅1', program=program)
        user1 = self.create_user('user1', 'user1@test.ai', 'password')
        user2 = self.create_user('user2', 'user2@test.ai', 'password')
        user3 = self.create_user('user3', 'user3@test.ai', 'password')
        user4 = self.create_user('user4', 'user4@test.ai', 'password')
        user5 = self.create_user('user5', 'user5@test.ai', 'password')

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
            'meetingId': get_global_id_from_object('Meeting', meeting.pk)
        }

        data = self.execute(gql, variables, user=user4)['participateMeeting']
        self.assertEqual(meeting.name, data['meetingParticipant']['meeting']['name'])
        self.assertEqual(user4.name, data['meetingParticipant']['participant']['name'])
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

    def test_program_tags(self):
        ProgramTag.objects.create(tag='2019년 4Q', type=ProgramTagTypeEnum.AFTERSCHOOL.value, is_active=False)

        gql = """
        query ProgramTags {
            programTags {
                tag
                type
            }
        }
        """

        data = self.execute(gql, user=self.user)['programTags']
        self.assertEqual(3, len(data))
        self.assertEqual('2020년 1Q', data[0]['tag'])
        self.assertEqual(ProgramTagTypeEnum.AFTERSCHOOL.name, data[0]['type'])

    def test_program(self):
        program = self.create_program(name='프로그램1',
                                      description='프로그램1설명입니다.',
                                      user=self.user,
                                      participants_max=4)
        member = self.create_user('user2', 'user2@test.ai', 'password')
        admin = self.create_user('user3', 'user3@test.ai', 'password', ManClassEnum.ADMIN.value)

        gql = """
        query Program($id:ID!) {
            program (id:$id) {
                name
                description
                isEditable
            }
        }
        """

        variables = {
            'id': get_global_id_from_object('Program', program.pk)
        }

        data = self.execute(gql, variables=variables, user=self.user)['program']
        self.assertTrue(data['isEditable'])
        data = self.execute(gql, variables=variables, user=member)['program']
        self.assertFalse(data['isEditable'])
        data = self.execute(gql, variables=variables, user=admin)['program']
        self.assertTrue(data['isEditable'])

    def test_zooms(self):
        program = self.create_program(name='프로그램1', description='프로그램1설명입니다.', user=self.user)
        zoom1 = self.create_zoom("Zoom1", 'zoom1@hanaui.net', 'hanaui', '123 456 7890', '1Nt',
                                 'https://us04web.zoom.us/j/1')
        zoom2 = self.create_zoom("Zoom2", 'zoom2@hanaui.net', 'hanaui', '123 456 7899', '2Nt',
                                 'https://us04web.zoom.us/j/2')

        self.create_meeting(name='미팅1',
                            program=program,
                            zoom=zoom1,
                            start_time=datetime(2020, 3, 1, 12, 0),
                            end_time=datetime(2020, 3, 1, 13, 0))

        self.create_meeting(name='미팅2',
                            program=program,
                            zoom=zoom2,
                            start_time=datetime(2020, 3, 1, 16, 0),
                            end_time=datetime(2020, 3, 1, 17, 0))

        self.create_meeting(name='미팅2',
                            program=program,
                            zoom=zoom1,
                            start_time=datetime(2020, 3, 10, 12, 0),
                            end_time=datetime(2020, 3, 10, 13, 0))

        self.create_meeting(name='미팅2',
                            program=program,
                            zoom=zoom1,
                            start_time=datetime(2020, 4, 10, 12, 0),
                            end_time=datetime(2020, 4, 10, 13, 0))

        gql = """
        query Zooms($year:Int!, $month:Int!, $day:Int) {
            zooms (year:$year, month:$month, day:$day) {
                startTime
                zoom {
                    meetingRoomId
                }
            }
        }
        """

        variables = {
            'year': 2020, 'month': 3
        }

        data = self.execute(gql, variables=variables, user=self.user)['zooms']
        self.assertEqual(3, len(data))

        variables = {
            'year': 2020, 'month': 4
        }
        data = self.execute(gql, variables=variables, user=self.user)['zooms']
        self.assertEqual(1, len(data))

        variables = {
            'year': 2020, 'month': 5
        }
        data = self.execute(gql, variables=variables, user=self.user)['zooms']
        self.assertEqual(0, len(data))

        variables = {
            'year': 2020, 'month': 3, 'day': 1
        }
        data = self.execute(gql, variables=variables, user=self.user)['zooms']
        self.assertEqual(2, len(data))

        variables = {
            'year': 2020, 'month': 4, 'day': 10
        }
        data = self.execute(gql, variables=variables, user=self.user)['zooms']
        self.assertEqual(1, len(data))

        variables = {
            'year': 2020, 'month': 4, 'day': 11
        }
        data = self.execute(gql, variables=variables, user=self.user)['zooms']
        self.assertEqual(0, len(data))
