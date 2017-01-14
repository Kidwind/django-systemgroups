# coding=UTF-8
from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _
from django.test import TestCase
from django.contrib.auth import get_user_model, get_permission_codename
from django.contrib.auth.models import Group, AnonymousUser, Permission
from django.conf import settings
from django.db import models

from .base import get_user_systemgroups, get_user_systemgroups_for_obj
from .systemgroups import SYSTEM_GROUP_EVERYONE, \
    SYSTEM_GROUP_ANONYMOUS, SYSTEM_GROUP_USERS, SYSTEM_GROUP_STAFFS, \
    SYSTEM_GROUP_CREATOR, SYSTEM_GROUP_OWNER
from .models import CreatorMixin, OwnerMixin
from .backends import SystemGroupBackend


class Info(CreatorMixin, OwnerMixin, models.Model):
    title = models.CharField(max_length=256, verbose_name=_('标题'))
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, verbose_name=_('创建者'))
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, verbose_name=_('所有者'))

    def get_creator(self):
        return self.creator

    def set_creator(self, user):
        self.creator = user

    def get_owner(self):
        return self.owner

    def set_owner(self, user):
        self.owner = user


class SystemGroupTestCaseMixin(object):
    def setUp(self):
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

        info = Info()
        info.title = "测试信息"
        info.set_creator(user)
        info.set_owner(user2)
        info.save()

        self.anonymous_user = AnonymousUser()
        self.user = user
        self.user2 = user2
        self.info = info


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
        self.assertNotIn(SYSTEM_GROUP_CREATOR, get_user_systemgroups_for_obj(self.anonymous_user, self.info))
        self.assertIn(SYSTEM_GROUP_CREATOR, get_user_systemgroups_for_obj(self.user, self.info))
        self.assertNotIn(SYSTEM_GROUP_CREATOR, get_user_systemgroups_for_obj(self.user2, self.info))

    def test_systemgroup_owner(self):
        self.assertNotIn(SYSTEM_GROUP_OWNER, get_user_systemgroups_for_obj(self.anonymous_user, self.info))
        self.assertNotIn(SYSTEM_GROUP_OWNER, get_user_systemgroups_for_obj(self.user, self.info))
        self.assertIn(SYSTEM_GROUP_OWNER, get_user_systemgroups_for_obj(self.user2, self.info))


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

        self.assertTrue(self.backend.has_perm(self.anonymous_user, 'auth.change_group', obj=self.info))
        self.assertFalse(self.backend.has_perm(self.anonymous_user, 'auth.delete_group', obj=self.info))
        self.assertTrue(self.backend.has_perm(self.user, 'auth.change_group', obj=self.info))
        self.assertFalse(self.backend.has_perm(self.user, 'auth.delete_group', obj=self.info))

    def test_systemgroup_anonymous(self):
        group = Group.objects.get_by_natural_key(SYSTEM_GROUP_ANONYMOUS)
        group.permissions.add(self.permission_delete_group)

        self.assertFalse(self.backend.has_perm(self.anonymous_user, 'auth.change_group', obj=self.info))
        self.assertTrue(self.backend.has_perm(self.anonymous_user, 'auth.delete_group', obj=self.info))
        self.assertFalse(self.backend.has_perm(self.user, 'auth.change_group', obj=self.info))
        self.assertFalse(self.backend.has_perm(self.user, 'auth.delete_group', obj=self.info))

    def test_systemgroup_users(self):
        group = Group.objects.get_by_natural_key(SYSTEM_GROUP_USERS)
        group.permissions.add(self.permission_change_group)
        group.permissions.add(self.permission_delete_group)

        self.assertFalse(self.backend.has_perm(self.anonymous_user, 'auth.change_group', obj=self.info))
        self.assertFalse(self.backend.has_perm(self.anonymous_user, 'auth.delete_group', obj=self.info))
        self.assertTrue(self.backend.has_perm(self.user, 'auth.change_group', obj=self.info))
        self.assertTrue(self.backend.has_perm(self.user, 'auth.delete_group', obj=self.info))

    def test_systemgroup_staffs(self):
        group = Group.objects.get_by_natural_key(SYSTEM_GROUP_STAFFS)
        group.permissions.add(self.permission_change_group)
        group.permissions.add(self.permission_delete_group)

        self.assertFalse(self.backend.has_perm(self.anonymous_user, 'auth.change_group', obj=self.info))
        self.assertFalse(self.backend.has_perm(self.anonymous_user, 'auth.delete_group', obj=self.info))
        self.assertFalse(self.backend.has_perm(self.user, 'auth.change_group', obj=self.info))
        self.assertFalse(self.backend.has_perm(self.user, 'auth.delete_group', obj=self.info))
        self.assertTrue(self.backend.has_perm(self.user2, 'auth.change_group', obj=self.info))
        self.assertTrue(self.backend.has_perm(self.user2, 'auth.delete_group', obj=self.info))

    def test_systemgroup_creator(self):
        group = Group.objects.get_by_natural_key(SYSTEM_GROUP_CREATOR)
        group.permissions.add(self.permission_change_group)
        group.permissions.add(self.permission_delete_group)

        self.assertFalse(self.backend.has_perm(self.anonymous_user, 'auth.change_group', obj=self.info))
        self.assertFalse(self.backend.has_perm(self.anonymous_user, 'auth.delete_group', obj=self.info))
        self.assertTrue(self.backend.has_perm(self.user, 'auth.change_group', obj=self.info))
        self.assertTrue(self.backend.has_perm(self.user, 'auth.delete_group', obj=self.info))
        self.assertFalse(self.backend.has_perm(self.user2, 'auth.change_group', obj=self.info))
        self.assertFalse(self.backend.has_perm(self.user2, 'auth.delete_group', obj=self.info))

    def test_systemgroup_owner(self):
        group = Group.objects.get_by_natural_key(SYSTEM_GROUP_OWNER)
        group.permissions.add(self.permission_change_group)
        group.permissions.add(self.permission_delete_group)

        self.assertFalse(self.backend.has_perm(self.anonymous_user, 'auth.change_group', obj=self.info))
        self.assertFalse(self.backend.has_perm(self.anonymous_user, 'auth.delete_group', obj=self.info))
        self.assertFalse(self.backend.has_perm(self.user, 'auth.change_group', obj=self.info))
        self.assertFalse(self.backend.has_perm(self.user, 'auth.delete_group', obj=self.info))
        self.assertTrue(self.backend.has_perm(self.user2, 'auth.change_group', obj=self.info))
        self.assertTrue(self.backend.has_perm(self.user2, 'auth.delete_group', obj=self.info))