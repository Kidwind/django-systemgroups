# coding=UTF-8
from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _
from django.test import TestCase
from django.contrib.auth import get_user_model, get_permission_codename
from django.contrib.auth.models import Group, AnonymousUser, Permission

from .base import get_user_systemgroups, get_user_systemgroups_for_obj
from .systemgroups import init_systemgroups, SYSTEM_GROUP_EVERYONE, \
    SYSTEM_GROUP_ANONYMOUS, SYSTEM_GROUP_USERS, SYSTEM_GROUP_STAFFS, \
    SYSTEM_GROUP_CREATOR, SYSTEM_GROUP_OWNER
from .models import CreatorMixin, OwnerMixin
from .backends import SystemGroupBackend


class SystemGroupTestCaseMixin(object):
    def setUp(self):
        init_systemgroups()

        User = get_user_model()

        user = User()
        user.username = 'tester'
        user.set_password('123456')
        user.is_staff = False
        user.save()

        user2 = User()
        user2.username = 'tester2'
        user2.set_password('123456')
        user2.is_staff = True
        user2.save()

        class ProxyGroup(CreatorMixin, OwnerMixin, Group):
            """
            因为系统组没有实现Creator和Owner相应的接口，因而建立测试代理组，用于测试创建者和所有者。
            """
            class Meta:
                proxy = True

            def get_creator(self):
                return user # 假设组对象的创建者均为 user

            def get_owner(self):
                return user2    # 假设组对象的所有者均为 user2

        self.anonymous_user = AnonymousUser()
        self.user = user
        self.user2 = user2
        self.group_obj = ProxyGroup.objects.get_by_natural_key(SYSTEM_GROUP_USERS)


class SystemGroupTestCase(SystemGroupTestCaseMixin, TestCase):
    def test_systemgroup_everyone(self):
        self.assertIn(SYSTEM_GROUP_EVERYONE, get_user_systemgroups(self.anonymous_user))
        self.assertIn(SYSTEM_GROUP_EVERYONE, get_user_systemgroups(self.user))

    def test_systemgroup_anonymous(self):
        self.assertIn(SYSTEM_GROUP_ANONYMOUS, get_user_systemgroups(self.anonymous_user))
        self.assertNotIn(SYSTEM_GROUP_ANONYMOUS, get_user_systemgroups(self.user))

    def test_systemgroup_users(self):
        self.assertNotIn(SYSTEM_GROUP_USERS, get_user_systemgroups(self.anonymous_user))
        self.assertIn(SYSTEM_GROUP_USERS, get_user_systemgroups(self.user))

    def test_systemgroup_staffs(self):
        self.assertNotIn(SYSTEM_GROUP_STAFFS, get_user_systemgroups(self.anonymous_user))
        self.assertNotIn(SYSTEM_GROUP_STAFFS, get_user_systemgroups(self.user))
        self.assertIn(SYSTEM_GROUP_STAFFS, get_user_systemgroups(self.user2))

    def test_systemgroup_creator(self):
        self.assertNotIn(SYSTEM_GROUP_CREATOR, get_user_systemgroups_for_obj(self.anonymous_user, self.group_obj))
        self.assertIn(SYSTEM_GROUP_CREATOR, get_user_systemgroups_for_obj(self.user, self.group_obj))
        self.assertNotIn(SYSTEM_GROUP_CREATOR, get_user_systemgroups_for_obj(self.user2, self.group_obj))

    def test_systemgroup_owner(self):
        self.assertNotIn(SYSTEM_GROUP_OWNER, get_user_systemgroups_for_obj(self.anonymous_user, self.group_obj))
        self.assertNotIn(SYSTEM_GROUP_OWNER, get_user_systemgroups_for_obj(self.user, self.group_obj))
        self.assertIn(SYSTEM_GROUP_OWNER, get_user_systemgroups_for_obj(self.user2, self.group_obj))


class SystemGroupBackendTestCase(SystemGroupTestCaseMixin, TestCase):
    def setUp(self):
        super(SystemGroupBackendTestCase, self).setUp()

        self.permission_change_group = Permission.objects.get_by_natural_key('change_group', Group._meta.app_label,
                                                                        Group._meta.model_name)
        self.permission_delete_group = Permission.objects.get_by_natural_key('delete_group', Group._meta.app_label,
                                                                        Group._meta.model_name)
        self.backend = SystemGroupBackend()

    def test_systemgroup_everyone(self):
        group = Group.objects.get_by_natural_key(SYSTEM_GROUP_EVERYONE)
        group.permissions.add(self.permission_change_group)

        self.assertTrue(self.backend.has_perm(self.anonymous_user, 'auth.change_group', obj=self.group_obj))
        self.assertFalse(self.backend.has_perm(self.anonymous_user, 'auth.delete_group', obj=self.group_obj))
        self.assertTrue(self.backend.has_perm(self.user, 'auth.change_group', obj=self.group_obj))
        self.assertFalse(self.backend.has_perm(self.user, 'auth.delete_group', obj=self.group_obj))

    def test_systemgroup_anonymous(self):
        group = Group.objects.get_by_natural_key(SYSTEM_GROUP_ANONYMOUS)
        group.permissions.add(self.permission_delete_group)

        self.assertFalse(self.backend.has_perm(self.anonymous_user, 'auth.change_group', obj=self.group_obj))
        self.assertTrue(self.backend.has_perm(self.anonymous_user, 'auth.delete_group', obj=self.group_obj))
        self.assertFalse(self.backend.has_perm(self.user, 'auth.change_group', obj=self.group_obj))
        self.assertFalse(self.backend.has_perm(self.user, 'auth.delete_group', obj=self.group_obj))

    def test_systemgroup_users(self):
        group = Group.objects.get_by_natural_key(SYSTEM_GROUP_USERS)
        group.permissions.add(self.permission_change_group)
        group.permissions.add(self.permission_delete_group)

        self.assertFalse(self.backend.has_perm(self.anonymous_user, 'auth.change_group', obj=self.group_obj))
        self.assertFalse(self.backend.has_perm(self.anonymous_user, 'auth.delete_group', obj=self.group_obj))
        self.assertTrue(self.backend.has_perm(self.user, 'auth.change_group', obj=self.group_obj))
        self.assertTrue(self.backend.has_perm(self.user, 'auth.delete_group', obj=self.group_obj))

    def test_systemgroup_staffs(self):
        group = Group.objects.get_by_natural_key(SYSTEM_GROUP_STAFFS)
        group.permissions.add(self.permission_change_group)
        group.permissions.add(self.permission_delete_group)

        self.assertFalse(self.backend.has_perm(self.anonymous_user, 'auth.change_group', obj=self.group_obj))
        self.assertFalse(self.backend.has_perm(self.anonymous_user, 'auth.delete_group', obj=self.group_obj))
        self.assertFalse(self.backend.has_perm(self.user, 'auth.change_group', obj=self.group_obj))
        self.assertFalse(self.backend.has_perm(self.user, 'auth.delete_group', obj=self.group_obj))
        self.assertTrue(self.backend.has_perm(self.user2, 'auth.change_group', obj=self.group_obj))
        self.assertTrue(self.backend.has_perm(self.user2, 'auth.delete_group', obj=self.group_obj))

    def test_systemgroup_creator(self):
        group = Group.objects.get_by_natural_key(SYSTEM_GROUP_CREATOR)
        group.permissions.add(self.permission_change_group)
        group.permissions.add(self.permission_delete_group)

        self.assertFalse(self.backend.has_perm(self.anonymous_user, 'auth.change_group', obj=self.group_obj))
        self.assertFalse(self.backend.has_perm(self.anonymous_user, 'auth.delete_group', obj=self.group_obj))
        self.assertTrue(self.backend.has_perm(self.user, 'auth.change_group', obj=self.group_obj))
        self.assertTrue(self.backend.has_perm(self.user, 'auth.delete_group', obj=self.group_obj))
        self.assertFalse(self.backend.has_perm(self.user2, 'auth.change_group', obj=self.group_obj))
        self.assertFalse(self.backend.has_perm(self.user2, 'auth.delete_group', obj=self.group_obj))

    def test_systemgroup_owner(self):
        group = Group.objects.get_by_natural_key(SYSTEM_GROUP_OWNER)
        group.permissions.add(self.permission_change_group)
        group.permissions.add(self.permission_delete_group)

        self.assertFalse(self.backend.has_perm(self.anonymous_user, 'auth.change_group', obj=self.group_obj))
        self.assertFalse(self.backend.has_perm(self.anonymous_user, 'auth.delete_group', obj=self.group_obj))
        self.assertFalse(self.backend.has_perm(self.user, 'auth.change_group', obj=self.group_obj))
        self.assertFalse(self.backend.has_perm(self.user, 'auth.delete_group', obj=self.group_obj))
        self.assertTrue(self.backend.has_perm(self.user2, 'auth.change_group', obj=self.group_obj))
        self.assertTrue(self.backend.has_perm(self.user2, 'auth.delete_group', obj=self.group_obj))