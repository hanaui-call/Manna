from datetime import datetime, timedelta

from django.contrib.auth.models import User

from django_server import const
from django_server import models


def create_user(email, username, role=const.ManClassEnum.MEMBER, password=None):
    if not password:
        password = username[0] + 'password!'

    user = User.objects.create_user(email=email, password=password, username=email)
    return models.Profile.objects.create(user=user, role=role.value)


def create_building(user, name, address, detailed_address, phone=''):
    return models.Building.objects.create(name=name,
                                          address=address,
                                          detailed_address=detailed_address,
                                          phone=phone,
                                          made_user=user)


def create_space(user, name, building):
    required_man_class = const.ManClassEnum.NON_MEMBER.value
    state = const.SpaceStateEnum.AVAILABLE.value

    return models.Space.objects.create(name=name,
                                       building=building,
                                       required_man_class=required_man_class,
                                       state=state,
                                       made_user=user)


def create_program(user, name, description, space=None):
    state = const.ProgramStateEnum.INVITING.value
    participants_min = 5
    participants_max = 10
    required_man_class = const.ManClassEnum.NON_MEMBER.value

    return models.Program.objects.create(name=name,
                                         description=description,
                                         space=space,
                                         state=state,
                                         participants_max=participants_max,
                                         participants_min=participants_min,
                                         required_man_class=required_man_class,
                                         owner=user)


def create_meeting(name, program):
    start_time = datetime.now() + timedelta(days=1)
    end_time = start_time + timedelta(hours=2)

    return models.Meeting.objects.create(name=name,
                                         program=program,
                                         start_time=start_time,
                                         end_time=end_time)


def clean_db():
    for x in [User, models.Building, models.Space, models.Program, models.Meeting]:
        x.objects.all().delete()


def run(*args):
    clean_db()
    user1 = create_user('admin.lee@dev.ai', 'Admin Lee', const.ManClassEnum.ADMIN)
    user2 = create_user('member.kim@dev.ai', 'Member Kim')

    building1 = create_building(user1, '하심재-만뜰', '서울 서대문구 가재울로 12', '지하1층')
    building2 = create_building(user1, '하심재-아뜰', '서울 서대문구 가재울로 12', '지하1층')

    building3 = create_building(user2, '가좌동-마을극장', '서울 서대문구 가재울로4길 39', '지하1층')
    building4 = create_building(user2, '따라멜리', '서울 서대문구 가재울로4길 39', '1층')
    building5 = create_building(user2, '하의재-마을사랑방', '서울 서대문구 가재울로4길 39', '2층')
    building6 = create_building(user2, '하의재-날자방', '서울 서대문구 가재울로4길 39', '2층')
    building7 = create_building(user2, '하의재-공육형님방', '서울 서대문구 가재울로4길 39', '2층')
    building8 = create_building(user2, '하의재-공육동생방', '서울 서대문구 가재울로4길 39', '2층')

    create_space(user1, '하심재-만뜰', building1)
    create_space(user1, '하심재-아뜰', building2)

    create_space(user2, '가좌동-마을극장', building3)
    create_space(user2, '하의재-날자방', building6)
    create_space(user2, '하의재-공육형님방', building7)
    create_space(user2, '하의재-공육동생방', building8)

    space1 = create_space(user2, '하의재-마을사랑방', building5)
    space2 = create_space(user2, '따라멜리', building4)

    program1 = create_program(
        user1,
        "좋은 삶을 고민하는 그리스도인",
        "그리스도인으로 사는 데 중요한 14가지 덕[자비, 진실함, 우정, 인내, 소망, 정의, 용기, 기쁨, 단순함, 한결같음, 겸손(과 유머), 절제, 너그러움, 믿음]에 대해서 같이 생각해보고 그리스도인답게 사는 것에 대해 나누어 보기.",
        space1
    )
    create_program(
        user2,
        "그리스도의 십자가 사역의 의미"
        "예수님의 십자가 사역의 의미와 우리에게 주는 다방면의 영향에 대해 탐구하면서 신앙의 토대를 다진다.",
        space2
    )

    create_meeting("강좌 소개 및 나누기", program1)
    create_meeting("자비, 진실함", program1)
    create_meeting("우정, 인내", program1)
    create_meeting("소망, 정의", program1)
    create_meeting("용기, 기쁨", program1)
    create_meeting("단순함, 한결같음", program1)
    create_meeting("겸손(과 유머), 절제", program1)
    create_meeting("너그러움, 믿음, 성품", program1)
