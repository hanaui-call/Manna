import logging

import graphene
from django.contrib import auth
from django.contrib.auth.models import User
from django.utils import timezone
from graphene_django import DjangoObjectType

from django_server import models
from django_server.const import ProgramStateEnum
from django_server.graphene.base import UserStatus, ManClass, Program, Meeting
from django_server.libs.authentification import AuthHelper, authorization

logger = logging.getLogger(__name__)


class Profile(DjangoObjectType):
    name = graphene.String(required=True)
    email = graphene.String(required=True)
    status = graphene.Field(UserStatus)
    role = graphene.Field(ManClass)
    programs = graphene.List(Program)
    meetings = graphene.List(Meeting)

    class Meta:
        model = models.Profile
        interfaces = (graphene.Node,)

    @staticmethod
    def resolve_name(root, info):
        return root.name

    @staticmethod
    def resolve_email(root, info):
        return root.user.email

    @staticmethod
    def resolve_status(root, info):
        return root.status

    @staticmethod
    def resolve_role(root, info, **kwargs):
        return root.role

    @staticmethod
    def resolve_programs(root, info, **kwargs):
        return [
            x.program for x in models.ProgramParticipant.objects.filter(participant=info.context.user)
            if x.program.state != ProgramStateEnum.END.value
        ]

    @staticmethod
    def resolve_meetings(root, info, **kwargs):
        today = timezone.now()
        return models.Meeting.objects.filter(start_time__gte=today,
                                             program__state=ProgramStateEnum.PROGRESS.value)[:3]


class Signin(graphene.Mutation):
    profile = graphene.Field(Profile)
    token = graphene.String()

    class Arguments:
        email = graphene.String(required=True)
        password = graphene.String(required=True)

    @staticmethod
    def mutate(root, info, **kwargs):
        email = kwargs.get('email')
        password = kwargs.get('password')

        try:
            user = User.objects.get(username=email)
            user = auth.authenticate(info.context, username=user.username, password=password)

            profile = models.Profile.objects.get(user=user)

            profile.last_login = timezone.now()
            profile.save()
            token = AuthHelper.generate_token({"user_id": str(profile.id)})
        except Exception:
            profile = None
            token = ""

        return Signin(profile=profile, token=token)


class Signup(graphene.Mutation):
    ok = graphene.Boolean()

    class Arguments:
        email = graphene.String(required=True)
        password = graphene.String(required=True)
        username = graphene.String(required=True)

    @staticmethod
    def mutate(root, info, **kwargs):
        email = kwargs.get('email')
        password = kwargs.get('password')
        username = kwargs.get('username')

        user = User.objects.create_user(email=email, password=password, username=email)
        models.Profile.objects.create(user=user, name=username)

        return Signup(ok=True)


class UserQuery(graphene.ObjectType):
    me = graphene.Field(Profile)

    @staticmethod
    @authorization
    def resolve_me(root, info, **kwargs):
        return info.context.user


class UserMutation(graphene.ObjectType):
    signin = Signin.Field()
    signup = Signup.Field()
