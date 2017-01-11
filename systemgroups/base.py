# coding=UTF-8
from __future__ import unicode_literals

import importlib
from django.contrib.auth.models import Permission, Group
from django.core.cache import cache
from django.db.models import signals

from .settings import SYSTEM_GROUP_IMPLEMENTERS


def get_user_systemgroups(user):
    """
    从所有应用中获取指定用户所属的系统组集合。
    :param user: 指定的用户。
    :return: set 表示的用户所属的系统组名称集合。
    """
    imps = SYSTEM_GROUP_IMPLEMENTERS
    groups = set()
    if not imps:
        return groups
    for imp in imps:
        imp = importlib.import_module(imp)
        if hasattr(imp, "get_user_systemgroups"):
            groups.update(imp.get_user_systemgroups(user))
    return groups


def get_user_systemgroups_for_obj(user, obj):
    """
    从所有应用中获取指定用户相对于指定的对象所属的系统组集合。
    :param user: 指定的用户。
    :param obj: 相对于指定的对象。
    :return: set 表示的用户所属的系统组名称集合。
    """
    imps = SYSTEM_GROUP_IMPLEMENTERS
    groups = set()
    if not imps:
        return groups
    for imp in imps:
        imp = importlib.import_module(imp)
        if hasattr(imp, "get_user_systemgroups_for_obj"):
            groups.update(imp.get_user_systemgroups_for_obj(user, obj))
    return groups


# 组权限缓存
def _build_group_permissions_cache_key(group_name):
    """
    根据组名构建组权限缓存键。
    :param group_name: 进行构建的组名。
    :return: 组权限缓存键。
    """
    return '__group_permissions_%s' % group_name


def _get_group_permissions(name):
    """
    获取指定名称的组所拥有的权限集合。
    :param name: 组的名称。
    :return: 权限集合。
    """
    perms = Permission.objects.filter(group__name = name)
    perms = perms.values_list('content_type__app_label', 'codename').order_by()
    return set(["%s.%s" % (ct, name) for ct, name in perms])


def _group_permissions_cache_clear_callback(sender, instance, **kwargs):
    """
    组权限缓存清除回调。
    """
    key = _build_group_permissions_cache_key(instance.name)
    cache.delete(key)
signals.post_save.connect(_group_permissions_cache_clear_callback, sender=Group)
signals.post_delete.connect(_group_permissions_cache_clear_callback, sender=Group)


def get_group_permissions(name):
    """
    获取指定名称的组所拥有的权限集合。
    :param name: 组的名称。
    :return: 权限集合。
    """
    key = _build_group_permissions_cache_key(name)
    perms = None
    if not key in cache:
        perms = _get_group_permissions(name)
        cache.set(key, perms)
    else:
        perms = cache.get(key)
    return perms


def get_groups_permissions(names):
    """
    获取指定名称的组所拥有的权限集合。
    :param names: 组的名称集合。
    :return: 权限集合。
    """
    perms = set()
    for name in names:
        perms.update(get_group_permissions(name))
    return perms