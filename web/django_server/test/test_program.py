import logging

from django_server.const import ProgramStateEnum, ManClassEnum
from django_server.graphene.utils import get_global_id_from_object
from django_server.test.test_base import BaseTestCase
from django_server.models import Program, Meeting

logger = logging.getLogger('__file__')


class SpaceTestCase(BaseTestCase):
    @classmethod
    def setUpTestData(cls):
        pass

    def setUp(self):
        self.clean_db()

    def test_create_program(self):
        space_name = '장소1'
        space = self.create_space(space_name)

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

        data = self.execute(gql, variables)['createProgram']['program']
        self.assertEqual(data['name'], variables['name'])
        self.assertEqual(data['description'], variables['description'])
        self.assertEqual(data['state'], variables['state'])
        self.assertEqual(data['openTime'], variables['openTime'])
        self.assertEqual(data['space']['name'], space_name)
        self.assertEqual(1, Program.objects.all().count())

    def test_update_program(self):
        program = self.create_program(name='프로그램1', description='프로그램1설명입니다.')

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

        data = self.execute(gql, variables)['updateProgram']['program']
        self.assertEqual(data['name'], variables['name'])
        self.assertEqual(data['description'], variables['description'])
        self.assertEqual(data['requiredManClass'], variables['requiredManClass'])
        self.assertEqual(data['openTime'], variables['openTime'])
        self.assertEqual(data['closeTime'], variables['closeTime'])

    def test_delete_program(self):
        program = self.create_program(name='프로그램1', description='프로그램1설명입니다.')

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

        ok = self.execute(gql, variables)['deleteProgram']['ok']
        self.assertTrue(ok)

        self.assertEqual(0, Program.objects.all().count())

    def test_create_meeting(self):
        program_name = '프로그램1'
        program = self.create_program(name=program_name, description='프로그램1설명입니다.')

        gql = """
        mutation CreateMeeting($name:String!, $programId:ID!, $startTime:DateTime!, $endTime:DateTime!) {
            createMeeting(name:$name, startTime:$startTime, endTime:$endTime, programId:$programId) {
                meeting {
                    name
                    startTime
                    endTime
                    program {
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
            'programId': get_global_id_from_object('Program', program.pk)
        }

        data = self.execute(gql, variables)['createMeeting']['meeting']
        self.assertEqual(data['name'], variables['name'])
        self.assertEqual(data['startTime'], variables['startTime'])
        self.assertEqual(data['endTime'], variables['endTime'])
        self.assertEqual(data['program']['name'], program_name)
        self.assertEqual(1, Program.objects.all().count())

    def test_update_meeting(self):
        meeting = self.create_meeting(name='미팅1')

        gql = """
        mutation UpdateMeeting($id:ID!, $name:String, $startTime:DateTime, $endTime:DateTime) {
            updateMeeting(id:$id, name:$name, startTime:$startTime, endTime:$endTime) {
                meeting {
                    name
                    startTime
                    endTime
                }
            }
        }
        """
        variables = {
            'name': 'meet1',
            'startTime': '2020-02-14T20:10:00+09:00',
            'endTime': '2020-02-14T21:10:00+09:00',
            'id': get_global_id_from_object('Meeting', meeting.pk)
        }

        data = self.execute(gql, variables)['updateMeeting']['meeting']
        self.assertEqual(data['name'], variables['name'])
        self.assertEqual(data['startTime'], variables['startTime'])
        self.assertEqual(data['endTime'], variables['endTime'])

    def test_delete_meeting(self):
        meeting = self.create_meeting(name='미팅1')

        gql = """
        mutation DeleteMeeting($id:ID!) {
            deleteMeeting(id:$id) {
                ok
            }
        }
        """
        variables = {
            'id': get_global_id_from_object('Meeting', meeting.pk),
        }

        self.assertEqual(1, Meeting.objects.all().count())

        ok = self.execute(gql, variables)['deleteMeeting']['ok']
        self.assertTrue(ok)

        self.assertEqual(0, Meeting.objects.all().count())
