from django.contrib.auth.models import User
from django.db import models

from django_server.const import ManClassEnum, SpaceStateEnum, ProgramStateEnum, UserStatusEnum


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Profile(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nickname = models.CharField(max_length=32, blank=True)
    status = models.CharField(max_length=1, default=UserStatusEnum.ACTIVE.value)
    last_signin = models.DateTimeField(null=True)
    role = models.CharField(max_length=1, default=ManClassEnum.MEMBER.value)

    def __str__(self):
        return f'{self.user.username}, {self.nickname}'


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
        address = f'{self.address} {self.detailed_adresss}'.strip()
        return f'{self.name}, {address}'


class Space(BaseModel):
    name = models.CharField(max_length=128, unique=True)
    building = models.ForeignKey(Building, on_delete=models.CASCADE)
    required_man_class = models.CharField(max_length=1, default=ManClassEnum.NON_MEMBER.value)
    state = models.CharField(max_length=1, default=SpaceStateEnum.WATING.value)
    made_user = models.ForeignKey(Profile, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f'{self.name}, {self.required_man_class}, {self.state}'


class Program(BaseModel):
    name = models.CharField(max_length=128)
    description = models.TextField(blank=True)
    space = models.ForeignKey(Space, on_delete=models.SET_NULL, null=True)
    state = models.CharField(max_length=1, default=ProgramStateEnum.READY.value)
    owner = models.ForeignKey(Profile, related_name='program', on_delete=models.SET_NULL, null=True)
    participants_min = models.IntegerField(default=1)
    participants_max = models.IntegerField(default=10)
    required_man_class = models.CharField(max_length=1, default=ManClassEnum.NON_MEMBER.value)
    open_time = models.DateTimeField()
    close_time = models.DateTimeField(null=True)
    is_after_school = models.BooleanField(default=False)
    # tags =
    # header_image =

    def __str__(self):
        return f'{self.name}, {self.required_man_class}, {self.state}'


class Meeting(BaseModel):
    name = models.CharField(max_length=128)
    program = models.ForeignKey(Program, related_name="meeting", on_delete=models.CASCADE)
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
