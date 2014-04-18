#!/usr/bin/env python

import time

from WebSocketClientManager import WebSocketClientManager
from WebSocketStructures import *

class WebSocketCmd():
    """
    Default Websocket command class.
    """
    # Command name
    cmd_name = None
    # Filtering object from colander
    filter = None
    # Answer to the command
    answer = None
    # Send cmd to queu before processing it.
    delayed_process = True
    # If the command need to be registred in the cmd pool for late processing.
    need_register = True

    def __init__(self, id, data, owner):
        """
        Init method.

        :param id: Command id.
        :type id: str.
        :param data: Command data structure.
        :type data: dict.
        """
        self.data = data
        self.cmd_id = id

    @classmethod
    def get_cmd_name(cls):
        """
        Return the class command name.

        :rtype: str.
        """
        if cls.cmd_name == None:
            raise ValueError("You need to set self.cmd_name according to your command name.")
        return cls.cmd_name

    def has_answer(self):
        """
        Check if the command have an answer to give to the client.

        :rtype: bool.
        """
        if self.answer:
            return True
        return False

    def filter_data(self):
        """
        Remove unused fields and check required ones from provided command data.

        :raise: ValueError with details if missing fields.
        """
        if self.filter == None:
            raise ValueError("self.filter can't be None ! It need to be a colander scheme.")
        self.data_filtered = self.filter().deserialize(self.data)
        return self.data_filtered

    def pre_process(self):
        """
        Method called before adding the command to queu.
        """
        raise NotImplementedError("You can't use the class WebSocketCmd as a WebSocket command, you need to create a subclass.")

    def process(self):
        """
        Method called on command processing.
        """
        raise NotImplementedError("You can't use the class WebSocketCmd as a WebSocket command, you need to create a subclass.")

# Debug
class WebSocketEchoCmd(WebSocketCmd):
    """
    Echo command. Give timestamp.
    """
    cmd_name = "echo"

    delayed_process = False

    def filter_data(self):
        pass

    def pre_process(self):
        self.answer = {"echo": str(time.time())}

    def process(self):
        self.pre_process()

# Debug
class WebSocketUserlistCmd(WebSocketCmd):
    """
    List other connected users.
    """
    cmd_name = "users_info"
    
    def filter_data(self):
        pass

    def pre_process(self):
        webSocketServer = WebSocketClientManager.instance()
        users = []
        for user in webSocketServer.get_instance_list():
            users.append({'ip': user['ip'],
                          'object': str(user['object']),
                          'connection_timestamp': user['connection_timestamp'],
                          'lastcmd_timestamp':  user['lastcmd_timestamp'],})
        self.answer = {'users': users}

    def process(self):
        self.pre_process()

