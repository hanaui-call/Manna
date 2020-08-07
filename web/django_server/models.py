from django.contrib.auth.models import User
import random
from django.db import models

from django_server.const import ManClassEnum, SpaceStateEnum, ProgramStateEnum, UserStatusEnum, ProgramTagTypeEnum


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Profile(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=32, blank=True)
    status = models.CharField(max_length=1, default=UserStatusEnum.ACTIVE.value)
    last_signin = models.DateTimeField(null=True)
    role = models.CharField(max_length=1, default=ManClassEnum.MEMBER.value)

    def __str__(self):
        return f'{self.user.username}, {self.name}'


class Building(BaseModel):
    name = models.CharField(max_length=128)
    address = models.CharField(max_length=128)
    detailed_address = models.CharField(max_length=64)
    phone = models.CharField(max_length=20, blank=True)
    made_user = models.ForeignKey(Profile, on_delete=models.SET_NULL, null=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['name', 'address'], name='building_constraint')
        ]

    def __str__(self):
        address = f'{self.address} {self.detailed_address}'.strip()
        return f'{self.name}, {address}'


class Space(BaseModel):
    name = models.CharField(max_length=128, unique=True)
    building = models.ForeignKey(Building, on_delete=models.CASCADE)
    required_man_class = models.CharField(max_length=1, default=ManClassEnum.NON_MEMBER.value)
    state = models.CharField(max_length=1, default=SpaceStateEnum.WATING.value)
    made_user = models.ForeignKey(Profile, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f'{self.name}, {self.required_man_class}, {self.state}'


class Zoom(BaseModel):
    name = models.CharField(max_length=128, unique=True)
    account_id = models.CharField(max_length=64, unique=True)
    account_pw = models.CharField(max_length=64)
    meeting_room_id = models.CharField(max_length=20, unique=True)
    meeting_room_pw = models.CharField(max_length=20)
    url = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return f'{self.name}, {self.url}'


class ProgramTag(BaseModel):
    tag = models.CharField(max_length=100, unique=True, default='ETC')
    is_active = models.BooleanField(default=True)
    type = models.CharField(max_length=1, default=ProgramTagTypeEnum.ETC.value)

    def __str__(self):
        return f'{self.tag} / ({self.is_active}) / {self.type}'


def get_default_no():
    return random.randint(0, 42)


class Program(BaseModel):
    name = models.CharField(max_length=128)
    description = models.TextField(blank=True)
    space = models.ForeignKey(Space, on_delete=models.SET_NULL, null=True)
    state = models.CharField(max_length=1, default=ProgramStateEnum.READY.value)
    owner = models.ForeignKey(Profile, related_name='program', on_delete=models.SET_NULL, null=True)
    participants_min = models.IntegerField(default=1)
    participants_max = models.IntegerField(default=10)
    required_man_class = models.CharField(max_length=1, default=ManClassEnum.NON_MEMBER.value)
    tag = models.ForeignKey(ProgramTag, on_delete=models.SET_NULL, null=True)
    image_no = models.IntegerField(default=get_default_no)

    class Meta:
        ordering = ['-modified_at']

    def __str__(self):
        return f'{self.name}, {self.required_man_class}, {self.state}'


class Meeting(BaseModel):
    name = models.CharField(max_length=128)
    program = models.ForeignKey(Program, related_name="meeting", on_delete=models.CASCADE)
    space = models.ForeignKey(Space, on_delete=models.SET_NULL, null=True)
    zoom = models.ForeignKey(Zoom, on_delete=models.SET_NULL, null=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f'{self.name}, ({self.program})'


class ProgramParticipant(BaseModel):
    program = models.ForeignKey(Program, related_name='program_participant', on_delete=models.CASCADE)
    participant = models.ForeignKey(Profile, related_name='program_participant', on_delete=models.SET_NULL, null=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['program', 'participant'], name='program_participant_constraint')
        ]


class MeetingParticipant(BaseModel):
    meeting = models.ForeignKey(Meeting, related_name='meeting_participant', on_delete=models.CASCADE)
    participant = models.ForeignKey(Profile, related_name='meeting_participant', on_delete=models.SET_NULL, null=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['meeting', 'participant'], name='meeting_participant_constraint')
        ]
