from collections import namedtuple
from functools import wraps

from graphql_relay.node.node import from_global_id

from django_server import models

Rid = namedtuple('Rid', 'name id')


def assign(args, obj, key):
    if key not in args:
        return

    setattr(obj, key, args[key])


def get_object_from_global_id(obj, global_id):
    rid = Rid(*from_global_id(global_id))
    return obj.objects.get(pk=rid.id)


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
