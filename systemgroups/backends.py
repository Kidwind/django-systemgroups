# coding=UTF-8
from __future__ import unicode_literals
from django.db import models
from .base import get_user_systemgroups, get_user_systemgroups_for_obj, get_groups_permissions


class SystemGroupBackend(object):
    def authenticate(self, username=None, password=None, **kwargs):
        return None

    def has_perm(self, user_obj, perm, obj=None):
        return perm in self.get_all_permissions(user_obj, obj)

    def get_all_permissions(self, user_obj, obj=None):
        perms = self.get_group_permissions(user_obj, obj)
        return perms

    def get_group_permissions(self, user_obj, obj=None):
        result_perms = set()

        if not hasattr(user_obj, '_systemgroup_perm_cache'):
            groups = get_user_systemgroups(user_obj)
            perms = get_groups_permissions(groups)
            user_obj._systemgroup_perm_cache = perms
        result_perms.update(user_obj._systemgroup_perm_cache)

        if obj is None:
            return result_perms

        if isinstance(obj, models.Model) and obj.pk is None:
            return result_perms

        if not hasattr(user_obj, '_systemgroup_perm_cache_for_obj'):
            user_obj._systemgroup_perm_cache_for_obj = {}
        if obj not in user_obj._systemgroup_perm_cache_for_obj:
            groups = get_user_systemgroups_for_obj(user_obj, obj)
            perms = get_groups_permissions(groups)
            user_obj._systemgroup_perm_cache_for_obj[obj] = perms
        result_perms.update(user_obj._systemgroup_perm_cache_for_obj[obj])
        return result_perms

    def has_module_perms(self, user_obj, app_label):
        """
        Return True if user_obj has any permissions in the given app_label.
        """
        if not user_obj.is_active:
            return False
        for perm in self.get_all_permissions(user_obj):
            if perm[:perm.index('.')] == app_label:
                return True
        return False
