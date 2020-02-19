import logging

from django_server.const import UserStatusEnum
from django_server.test.test_base import BaseTestCase

from django.contrib.auth.models import User
from django_server.models import Profile


logger = logging.getLogger('__file__')


class UserTestCase(BaseTestCase):
    def test_signup(self):
        email = 'kdhong@test.ai'
        username = '홍길동'
        password = 'password'
        nickname = '홍짱'
        gql = """
        mutation Signup($email:String!, $username:String!, $password:String!, $nickname:String) {
            signup(email:$email, username:$username, password:$password, nickname:$nickname) {
                ok
            }
        }
        """
        variables = {
            'email': email,
            'username': username,
            'password': password,
            'nickname': nickname
        }

        ok = self.execute(gql, variables)['signup']['ok']
        self.assertTrue(ok)

        user = User.objects.get(email=email)
        profile = Profile.objects.get(user=user)

        self.assertEqual(email, user.email)
        self.assertEqual(username, user.username)
        self.assertEqual(nickname, profile.nickname)
        self.assertEqual(UserStatusEnum.ACTIVE.value, profile.status)

    def test_signin(self):
        email = 'kdhong@test.ai'
        username = '홍길동'
        nickname = '홍짱'

        self.create_user(username=username, email=email, nickname=nickname)

        gql = """
        mutation Signin($email:String!, $password:String!) {
            signin(email:$email, password:$password) {
                token
                profile {
                    name
                    nickname
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
        self.assertEqual(nickname, data['profile']['nickname'])

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
                nickname
            }
        }
        """

        data = self.execute(gql, user=self.user)['me']
        self.assertEqual(self.user.user.email, data['email'])
        self.assertEqual(self.user.nickname, data['nickname'])
