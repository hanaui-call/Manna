import logging
from datetime import datetime
from freezegun import freeze_time

from django_server.const import UserStatusEnum, ManClassEnum, ProgramStateEnum, MannaError
from django_server.test.test_base import BaseTestCase

from django.contrib.auth.models import User
from django_server.models import Profile, ProgramParticipant


logger = logging.getLogger('__file__')


@freeze_time('2020-04-01 12:00:00')
class UserTestCase(BaseTestCase):
    def test_signup(self):
        email = 'kdhong@test.ai'
        username = '홍길동'
        password = 'password'
        gql = """
        mutation Signup($email:String!, $username:String!, $password:String!) {
            signup(email:$email, username:$username, password:$password) {
                ok
            }
        }
        """
        variables = {
            'email': email,
            'username': username,
            'password': password,
        }

        ok = self.execute(gql, variables)['signup']['ok']
        self.assertTrue(ok)

        user = User.objects.get(email=email)
        profile = Profile.objects.get(user=user)

        self.assertEqual(email, user.email)
        self.assertEqual(username, profile.name)
        self.assertEqual(UserStatusEnum.ACTIVE.value, profile.status)

    def test_signin(self):
        email = 'kdhong@test.ai'
        username = '홍길동'

        self.create_user(username=username, email=email)

        gql = """
        mutation Signin($email:String!, $password:String!) {
            signin(email:$email, password:$password) {
                token
                profile {
                    name
                    email
                }
            }
        }
        """
        variables = {
            'email': email,
            'password': 'password',
        }

        data = self.execute(gql, variables)['signin']
        self.assertNotEqual("", data['token'])
        self.assertEqual(email, data['profile']['email'])
        self.assertEqual(username, data['profile']['name'])

        variables = {
            'email': email,
            'password': 'passwo',       # wrong password
        }

        data = self.execute(gql, variables)['signin']
        self.assertEqual("", data['token'])
        self.assertIsNone(data['profile'])

    def test_me(self):
        program1 = self.create_program(name='프로그램1', description='프로그램1설명입니다.', user=self.user)
        program2 = self.create_program(name='프로그램2',
                                       description='프로그램2설명입니다.',
                                       space=program1.space,
                                       user=self.user,
                                       state=ProgramStateEnum.END.value)

        ProgramParticipant.objects.create(program=program1, participant=self.user)
        ProgramParticipant.objects.create(program=program2, participant=self.user)

        self.create_meeting(name='미팅1',
                            program=program1,
                            start_time=datetime(2020, 4, 1, 12, 0),
                            end_time=datetime(2020, 4, 1, 13, 0))

        self.create_meeting(name='미팅2',
                            program=program1,
                            start_time=datetime(2020, 4, 1, 16, 0),
                            end_time=datetime(2020, 4, 1, 17, 0))

        self.create_meeting(name='미팅3',
                            program=program1,
                            start_time=datetime(2020, 4, 10, 12, 0),
                            end_time=datetime(2020, 4, 10, 13, 0))

        self.create_meeting(name='미팅1',
                            program=program2,
                            start_time=datetime(2020, 4, 8, 12, 0),
                            end_time=datetime(2020, 4, 8, 13, 0))

        gql = """
        query Me {
            me {
                email
                role
                programs {
                    name
                }
                meetings {
                    name
                }
            }
        }
        """

        data = self.execute(gql, user=self.user)['me']
        self.assertEqual(self.user.user.email, data['email'])
        self.assertEqual(ManClassEnum.MEMBER.name, data['role'])
        self.assertEqual(1, len(data['programs']))
        self.assertEqual(3, len(data['meetings']))
        for i, x in enumerate(data['meetings'], 1):
            self.assertEqual(f'미팅{i}', x['name'])

    def test_reset_password(self):
        email = 'kdhong@test.ai'
        username = '홍길동'

        user = self.create_user(username=username, email=email)

        gql = """
        mutation ResetPassword($oldPassword:String!, $newPassword:String!) {
            resetPassword(oldPassword:$oldPassword, newPassword:$newPassword) {
                error {
                    key
                }
                ok
            }
        }
        """
        variables = {
            'oldPassword': 'passwor',
            'newPassword': 'new_password',
        }

        data = self.execute(gql, variables, user=user)['resetPassword']
        self.assertEqual(MannaError.INVALID_PERMISSION.name, data['error']['key'])

        variables = {
            'oldPassword': 'password',
            'newPassword': 'new_password',
        }

        ok = self.execute(gql, variables, user=user)['resetPassword']['ok']
        self.assertTrue(ok)
