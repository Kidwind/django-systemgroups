# coding=UTF-8
from __future__ import unicode_literals

from django.utils.translation import ugettext as _


class CreatorMixin(object):
    """
    实现创建者的 Model 基类。
    """
    def get_creator(self):
        """
        获取对象的创建者，子类重写该方法实现创建者对象的获取。
        :return: 当前对象的创建者。
        """
        return None

    def set_creator(self, user):
        """
        设置对象的创建者，子类重写该方法实现创建者对象的设置。
        :param creator: 要设置为创建者的User对象。
        :return:
        """
        pass


class OwnerMixin(object):
    """
    实现所有者的 Model 基类。
    """
    def get_owner(self):
        """
        获取对象的所有者，子类重写该方法实现所有者对象的获取。
        :return: 当前对象的所有者。
        """
        return None

    def set_owner(self, user):
        """
        设置对象的所有者，子类重写该方法实现所有者对象的设置。
        :param owner: 要设置为所有者的User对象。
        :return:
        """
        pass