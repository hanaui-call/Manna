import logging

from django_server.const import ProgramStateEnum, ManClassEnum
from django_server.graphene.utils import get_global_id_from_object
from django_server.test.test_base import BaseTestCase
from django_server.models import Program, Meeting

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
