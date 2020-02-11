from django.contrib.auth.models import User
from django.db import models

from django_server.const import ManClassEnum, SpaceStateEnum


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Profile(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nickname = models.CharField(max_length=32, blank=True)

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
