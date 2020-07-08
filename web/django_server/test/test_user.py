import logging

from django_server.const import UserStatusEnum, ManClassEnum
from django_server.test.test_base import BaseTestCase

from django.contrib.auth.models import User
from django_server.models import Profile


logger = logging.getLogger('__file__')


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
        gql = """
        query Me {
            me {
                email
                role
            }
        }
        """

        data = self.execute(gql, user=self.user)['me']
        self.assertEqual(self.user.user.email, data['email'])
        self.assertEqual(ManClassEnum.MEMBER.name, data['role'])
