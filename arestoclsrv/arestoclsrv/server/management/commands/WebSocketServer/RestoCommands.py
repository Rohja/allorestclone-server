#!/usr/bin/env python

from WebSocketCommand import WebSocketCmd

from arestoclsrv.server.models import *
from arestoclsrv.server.serializers import *

# SPECIAL: AUTH
from django.contrib.auth import authenticate
from django.contrib.auth.models import User

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
            self.error = "Missing username or password."
        else:
            user = authenticate(username=self.data['username'], password=self.data['password'])
            if user:
                self.raw_user = user
                user = UserSerializer(user)
                user = user.data
            self.answer = {"user": user}

    def process(self):
        self.pre_process()


class CreateUserCmd(WebSocketCmd):
    cmd_name = "user_create"

    delayed_process = False

    raw_user = None

    def filter_data(self):
        # FIXME: Add colander filtering.
        pass

    def pre_process(self):
        # self.answer = {"echo": str(time.time())}
        if not self.data.get('username'):
            self.error = "Missing username."
        elif not self.data.get('password'):
            self.error = "Missing password."
        elif not self.data.get('email'):
            self.error = "Missing email."
        elif not self.data.get('phone'):
            self.error = "Missing phone number."    
        else:
            try:
                user = User.objects.get(username=self.data['username'])
            except User.DoesNotExist:
                # GOOD
                user = User(username=self.data['username'],
                            email=self.data['email'])
                user.set_password(self.data['password'])
                user.is_active = True
                user.save()
                user = UserSerializer(user)
                self.answer = {"user": user.data}
            else:
                self.error = "Username already in use."

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
            self.error = "Missing user id."
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
