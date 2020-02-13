import logging
from collections import namedtuple
from functools import wraps

from graphql_relay.node.node import from_global_id, to_global_id

from django_server import models

logger = logging.getLogger('__file__')

Rid = namedtuple('Rid', 'name id')


def assign(args, obj, key):
    if key not in args:
        return

    setattr(obj, key, args[key])


def get_global_id_from_object(type_name, local_id):
    return to_global_id(type_name, local_id)


def get_local_id_from_global_id(global_id):
    rid = Rid(*from_global_id(global_id))
    return rid.id


def get_object_from_global_id(obj, global_id):
    if not global_id:
        return None
    return obj.objects.get(pk=get_local_id_from_global_id(global_id))


def has_building(func):
    @wraps(func)
    def wrap(root, info, **kwargs):
        info.context.building = get_object_from_global_id(models.Building, kwargs.get('id'))
        return func(root, info, **kwargs)
    return wrap


def has_space(func):
    @wraps(func)
    def wrap(root, info, **kwargs):
        info.context.space = get_object_from_global_id(models.Space, kwargs.get('id'))
        return func(root, info, **kwargs)
    return wrap


def has_program(func):
    @wraps(func)
    def wrap(root, info, **kwargs):
        info.context.program = get_object_from_global_id(models.Program, kwargs.get('id'))
        return func(root, info, **kwargs)
    return wrap
