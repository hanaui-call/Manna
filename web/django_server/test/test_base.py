import logging
from datetime import datetime, timedelta

from django.contrib.auth.models import User
from django.test import TestCase

from django_server.const import SpaceStateEnum, ManClassEnum, ProgramStateEnum, ProgramTagTypeEnum
from django_server.models import Profile, Building, Space, Program, Meeting, ProgramTag, Zoom
from django_server.schema import schema

logger = logging.getLogger(__name__)


class Context(object):
    def __init__(self):
        pass


class BaseTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        ProgramTag.objects.create(tag='2020년 1Q', type=ProgramTagTypeEnum.AFTERSCHOOL.value)
        ProgramTag.objects.create(tag='마을', type=ProgramTagTypeEnum.TOWN.value)
        ProgramTag.objects.create(tag='기타', type=ProgramTagTypeEnum.ETC.value)

    def setUp(self):
        self.clean_db()
        self.user = self.create_user(username='TestAdmin',
                                     email='test_admin@test.ai')

    @staticmethod
    def clean_db():
        for x in [User, Building, Space, Program, Meeting]:
            x.objects.all().delete()

    @staticmethod
    def execute(gql, variables=None, user=None):
        context = Context()
        if user:
            context.user = user

        result = schema.execute(gql, variables=variables, context=context)
        if result.errors:
            raise Exception(result.errors)
        return result.data

    @staticmethod
    def create_user(username='Test', email='test@test.ai', password='password', role=ManClassEnum.MEMBER.value):
        user = User.objects.create_user(username=email, email=email, password=password)
        return Profile.objects.create(user=user, name=username, role=role)

    def create_building(self, name='기본빌딩', address='서울시', detailed_address='123층', phone='12-1234', user=None):
        if not user:
            user = self.create_user(username='building_man', email='building_man@test.ai')

        return Building.objects.create(name=name,
                                       address=address,
                                       detailed_address=detailed_address,
                                       phone=phone,
                                       made_user=user)

    def create_space(self, name='기본장소', building=None, required_man_class=ManClassEnum.NON_MEMBER.value,
                     state=SpaceStateEnum.WATING.value, user=None):
        if not user:
            user = self.create_user(username='space_man', email='space_man@test.ai')
        if not building:
            building = self.create_building(user=user)

        return Space.objects.create(name=name,
                                    building=building,
                                    required_man_class=required_man_class,
                                    state=state,
                                    made_user=user)

    @staticmethod
    def create_zoom(name, account_id, account_pw, meeting_room_id, meeting_room_pw, url):
        return Zoom.objects.create(name=name,
                                   account_id=account_id,
                                   account_pw=account_pw,
                                   meeting_room_id=meeting_room_id,
                                   meeting_room_pw=meeting_room_pw,
                                   url=url)

    def create_program(self, name='기본프로그램', description='', space=None,
                       required_man_class=ManClassEnum.NON_MEMBER.value,
                       state=ProgramStateEnum.PROGRESS.value, user=None, participants_min=1, participants_max=10,
                       tag=None):
        if not user:
            user = self.create_user(username='program_man', email='program_man@test.ai')
        if not space:
            space = self.create_space(user=user)

        if not tag:
            tag = ProgramTag.objects.first()

        return Program.objects.create(name=name,
                                      description=description,
                                      space=space,
                                      state=state,
                                      participants_max=participants_max,
                                      participants_min=participants_min,
                                      required_man_class=required_man_class,
                                      owner=user,
                                      tag=tag)

    def create_meeting(self, name='기본프로그램', program=None,
                       start_time=datetime.now(), end_time=datetime.now() + timedelta(hours=1), space=None, zoom=None):
        if not program:
            program = self.create_program()

        if not space:
            space = program.space

        return Meeting.objects.create(name=name,
                                      program=program,
                                      start_time=start_time,
                                      end_time=end_time,
                                      space=space,
                                      zoom=zoom)
