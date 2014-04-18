#!/usr/bin/env python

from WebSocketCommand import WebSocketCmd

from arestoclsrv.server.models import *
from arestoclsrv.server.serializers import *

# SPECIAL: AUTH
from django.contrib.auth import authenticate

class AuthUsersCmd(WebSocketCmd):
    """
    Authentification cmd
    require username and password (both strings)
    """
    cmd_name = "user_auth"

    delayed_process = False

    raw_user = None

    def filter_data(self):
        # FIXME: Add colander filtering.
        pass

    def pre_process(self):
        # self.answer = {"echo": str(time.time())}
        if not self.data.get('username') or not self.data.get('password'):
            user = None
        else:
            user = authenticate(username=self.data['username'], password=self.data['password'])
            if user:
                self.raw_user = user
                user = UserSerializer(user)
                user = user.data
        self.answer = {"user": user}

    def process(self):
        self.pre_process()


## RestoUser
# GET
class GetRestoUsersCmd(WebSocketCmd):
    """
    Echo command. Give timestamp.
    """
    cmd_name = "restouser_get"

    delayed_process = False

    def filter_data(self):
        # FIXME: Add colander filtering.
        pass

    def pre_process(self):
        # self.answer = {"echo": str(time.time())}
        if not self.data.get('id'):
            user = None
        else:
            try:
                user = RestoUser.objects.get(id=self.data['id'])
            except RestoUser.DoesNotExist:
                user = None
            else:
                user = RestoUserSerializer(user)
        if user:
            user = user.data
        self.answer = {"user": user}

    def process(self):
        self.pre_process()
