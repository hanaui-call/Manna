from django.contrib.auth.models import User
from django.test import TestCase

from django_server.models import Profile, Building, Space
from django_server.schema import schema
from django_server.const import SpaceStateEnum, ManClassEnum


class Context(object):
    def __init__(self):
        pass


class BaseTestCase(TestCase):
    @staticmethod
    def clean_db():
        for x in [User, Building, Space]:
            x.objects.all().delete()

    @staticmethod
    def execute(gql, variables=None):
        context = Context()
        result = schema.execute(gql, variables=variables, context=context)
        if result.errors:
            raise Exception(result.errors)
        return result.data

    @staticmethod
    def create_user(username='Test', email='test@test.ai', nickname='testking'):
        user = User.objects.create_user(username=username, email=email)
        return Profile.objects.create(user=user, nickname=nickname)

    def create_building(self, name='기본빌딩', address='서울시', detailed_address='123층', phone='12-1234', user=None):
        if not user:
            user = self.create_user(username='building_man', email='building_man@test.ai', nickname='building_man')

        return Building.objects.create(name=name,
                                       address=address,
                                       detailed_address=detailed_address,
                                       phone=phone,
                                       made_user=user)

    def create_space(self, name='기본장소', building=None, required_man_class=ManClassEnum.NON_MEMBER.value,
                     state=SpaceStateEnum.WATING.value, user=None):
        if not user:
            user = self.create_user(username='space_man', email='space_man@test.ai', nickname='space_man')
        if not building:
            building = self.create_building(user=user)

        return Space.objects.create(name=name,
                                    building=building,
                                    required_man_class=required_man_class,
                                    state=state,
                                    made_user=user)