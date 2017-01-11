# coding=UTF-8
from __future__ import unicode_literals

from django.contrib.auth.models import Group

from .models import CreatorMixin, OwnerMixin


SYSTEM_GROUP_EVERYONE = "Everyone"      # 所有人
SYSTEM_GROUP_ANONYMOUS = "Anonymous"    # 匿名用户
SYSTEM_GROUP_USERS = "Users"            # 用户
SYSTEM_GROUP_STAFFS = "Staffs"          # 职员
SYSTEM_GROUP_CREATOR = "Creator"        # 创建者
SYSTEM_GROUP_OWNER = "Owner"            # 所有者


def init_systemgroups():
    """
    初始化系统组。
    :return:
    """
    Group.objects.get_or_create(name=SYSTEM_GROUP_EVERYONE)
    Group.objects.get_or_create(name=SYSTEM_GROUP_ANONYMOUS)
    Group.objects.get_or_create(name=SYSTEM_GROUP_USERS)
    Group.objects.get_or_create(name=SYSTEM_GROUP_STAFFS)
    Group.objects.get_or_create(name=SYSTEM_GROUP_CREATOR)
    Group.objects.get_or_create(name=SYSTEM_GROUP_OWNER)


def get_user_systemgroups(user):
    """
    获取指定用户所属的系统组集合。
    :param user: 指定的用户。
    :return: set 表示的用户所属的系统组名称集合。
    """
    groups = set()
    groups.add(SYSTEM_GROUP_EVERYONE)
    if user.is_anonymous():
        groups.add(SYSTEM_GROUP_ANONYMOUS)
    else:
        groups.add(SYSTEM_GROUP_USERS)
        if user.is_staff:
            groups.add(SYSTEM_GROUP_STAFFS)

    return groups

def get_user_systemgroups_for_obj(user, obj):
    """
    获取指定用户相对于指定的对象所属的系统组集合。
    :param user: 指定的用户。
    :param obj: 相对于指定的对象。
    :return: set 表示的用户所属的系统组名称集合。
    """
    groups = set()
    if isinstance(obj, CreatorMixin) and obj.get_creator() == user:
        groups.add(SYSTEM_GROUP_CREATOR)
    if isinstance(obj, OwnerMixin) and obj.get_owner() == user:
        groups.add(SYSTEM_GROUP_OWNER)
    return groups