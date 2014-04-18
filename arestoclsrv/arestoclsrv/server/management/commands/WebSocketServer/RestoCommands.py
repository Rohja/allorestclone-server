#!/usr/bin/env python

from WebSocketCommand import WebSocketCmd

from arestoclsrv.server.models import *
from arestoclsrv.server.serializers import *

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

