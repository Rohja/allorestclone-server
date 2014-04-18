#!/usr/bin/env python

# Python
import json
import time
import md5
import copy
# Libs
import tornado.httpserver
from tornado import websocket
import tornado.ioloop
import tornado.web
import colander
# NM
from WebSocketClientManager import WebSocketClientManager
from WebSocketCommand import *
#
from RestoCommands import *

class WebSocketClient(websocket.WebSocketHandler):
    """
    WebSocketClient represent a user connected to the WebSocket server of Node Manager.
    """
    cmd_list = {} # {"intel": WebSocketIntelCmd, ... }
    django_user = None

    def __init__(self, *argv, **kwargs):
        """
        Initialize WebSocketClient.
        """
        print "WebSocketClient.__init__(): self = %s" % self
        super(WebSocketClient, self).__init__(*argv, **kwargs)

    def __unicode__(self):
        return u"%s" % self

    @classmethod
    def register_cmd(cls, cmdclass, type='all'):
        """
        Register command to the class. (Add cmd name and cmd object to cls.cmd_list.
        :param cmdname: Name of the command.
        :type cmdname: str.
        :param cmdclass: Class to register.
        :type cmdclass: WebSocketCmd.
        """
        print "WebSocketClient<class>.register_cmd():"
        if not issubclass(cmdclass, WebSocketCmd):
            print " -- %s in not a valid commmand !" % cmdname
            return
        cmdname = cmdclass.get_cmd_name()
        if type not in ['all', 'auth']:
            raise ValueError("Type can only be 'all' or 'auth'")
        if type not in cls.cmd_list:
            cls.cmd_list[type] = {}
        if cmdname in cls.cmd_list[type]:
            print " -- %s already exist in cmd_list." % cmdname
            print " -- cmd_list: ",cls.cmd_list[type]
            return
        print "-- new command (%s, %s, %s)" % (cmdname, cmdclass, type)
        cls.cmd_list[type][cmdname] = cmdclass

    def _send_message(self, message):
        """
        Send message to client.
        :param message: Message to send.
        :type message: str.
        """
        print "WebSocketClient.__init__(): self = %s" % self
        print " -- message = %s" % message
        self.write_message(message)

    def _generate_cmd_id(self, command):
        print "WebSocketClient._generate_cmd_id(): self = %s" % self
        print " -- command = %s" % command
        current_time = time.time()
        text_id = "%s_%f" % (command, current_time)
        print " -- text_id = %s" % text_id
        md5_id = md5.new()
        md5_id.update(text_id)
        md5_text_id = md5_id.hexdigest()
        print " -- ms5_id = %s" % md5_text_id
        return md5_text_id

    def _get_valid_cmd_data(self, message):
        """
        Get a json string and try to loads it to Python.
        :param message: Json string.
        :type message: str.
        :rtype: None or str.
        """
        print "WebSocketClient._get_valid_cmd_data(): self = %s" % self
        try:
            message_data = json.loads(message)
        except ValueError:
            print "WebSocketClient._get_valid_cmd_data(): self = %s" % self
            print " -- BAD JSON CONTENT TO DUMPS"
            return None
        if not message_data.get("cmd"):
            print "WebSocketClient._get_valid_cmd_data(): self = %s" % self
            print " -- NO CMD IN DICT"
            return None
        return (message_data["cmd"], message_data)

    def _gen_ans(self, cmdinstance, to_message=True):
        """
        Create an answer fron WebSockectCmd instance.

        :param cmdinstance: Instance of WebSocketCmd with valid answer.
        :type cmdinstance: Instance of subclass of WebSocketCmd.
        :return: Text answer (json formated).
        :rtype: str or None (if error).
        """
        if cmdinstance.answer:
            answer_data = cmdinstance.answer
        else:
            answer_data = {}
        answer_data['ans'] = cmdinstance.get_cmd_name()
        answer_data['id'] = cmdinstance.cmd_id
        if to_message:
            try:
                answer_text = json.dumps(answer_data)
            except ValueError:
                return None
            return answer_text
        return answer_data

    def _gen_ans_message(self, cmdinstance, msgtype, msgtext):
        """
        Create a answer message from WebSocketCmd instance.

        :param cmdinstance: Instance of subclass of WebSocketCmd.
        :type cmdinstance: Instance of subclass of WebSocketCmd.
        :param msgtype: Message type.
        :type msgtype: str.
        :paran msgtext: Message text.
        :type msgtext: str.
        """
        answer_data = self._gen_ans(cmdinstance, to_message=False)
        answer_data['msg_type'] = msgtype
        answer_data['msg_text'] = msgtext
        try:
            answer_text = json.dumps(answer_data)
        except ValueError:
            return None
        return answer_text

    def _gen_ack(self, cmd, id, to_message=True):
        """
        Generate ack message to send to the client.

        :param cmd: Command.
        :type cmd: str.
        :param id: Command instance unique ID.
        :type id: str.
        :param msg: Message details.
        :type msg: str.
        :return: Message to send to the client (json formated or python dict).
        :rtype: None or str.
        """
        print "WebSocketClient._create_error_ack(): self = %s" % self

        message = {"ack": str(cmd)}

        if id:
            print " -- id = %s" % id
            message['id'] = str(id)
        else:
            print " -- id is None"

        if to_message:
            try:
                json_message = json.dumps(message)
            except ValueError:
                print "WebSocketClient._gen_ack(): self = %s" % self
                print " -- BAD JSON CONTENT TO DUMPS"
                return None
            return json_message
        return message

    def _gen_ack_message(self, cmd, id, type, msg):
        """
        Generate ack message (info/warn/error/debug) to send to the client.

        :param cmd: Command name.
        :type cmd: str.
        :param id: Command instance unique id.
        :type id: str.
        :param type: Type of message.
        :type type: str.
        :param msg: Message text.
        :type msg: str.
        :return: Ack message to send.
        :rtype: str or None (if error).
        """
        ack = self._gen_ack(cmd, id, to_message=False)
        ack["msg_type"] = str(type)
        ack["msg_text"] = str(msg)
        try:
            ack_json = json.dumps(ack)
        except ValueError:
            print "WebSocketClient._gen_ack_message(): self = %s" % self
            print " -- BAD JSON CONTENT TO DUMPS"
            return None
        return ack_json

    def _gen_ans_message2(self, cmd, id, type, msg):
        ack = self._gen_ack(cmd, id, to_message=False)
        ack_cmd = ack['ack']
        del ack['ack']
        ack['ans'] = ack_cmd
        ack["msg_type"] = str(type)
        ack["msg_text"] = str(msg)
        try:
            ack_json = json.dumps(ack)
        except ValueError:
            print "WebSocketClient._gen_ack_message(): self = %s" % self
            print " -- BAD JSON CONTENT TO DUMPS"
            return None
        return ack_json


    def open(self):
        """
        Called on client connection.
        Register itself to the WebSocketClientManager instance.
        """
        print "WebSocketClient.open(): self = %s" % self

    def _process_cmd(self, cmd_name, cmd_id, cmd_data):
        """
        Process cmd with provided data.

        :param cmd_name: Command name.
        :type cmd_name: str.
        :param cmd_id: Command instance unique id.
        :type cmd_id: str.
        :param cmd_data: Command data provided by user.
        :type cmd_data: dict.
        """
        print "WebSocketClient._process_cmd(): self = %s"
        print " -- cmd_name: ", cmd_name
        print " -- cmd_id: ", cmd_id
        print " -- cmd_data: ", cmd_data
        self._send_message(self._gen_ack(cmd_name, cmd_id))
        # FIXME: Add auth. change type + method to find right cmd directory
        cmd_instance = self._find_command(cmd_name)(cmd_id, cmd_data, self)
        #
        cmd_instance.django_user = self.django_user
        #
        try:
            cmd_instance.filter_data()
        except colander.Invalid, e:
            print " -- Colander error: ", e
            self._send_message(self._gen_ans_message(cmd_instance, "error", "Invalid or missing parameters"))
            return
        cmd_instance.pre_process()
        # SPECIAL CMDS
        # Auth.
        if cmd_name == "user_auth" and cmd_instance.raw_user:
            self.django_user = cmd_instance.raw_user
            print " -- INFO: USER AUTHENTICATED !"
        #
        #
        if cmd_instance.has_answer():
            print " -- cmd_instance.answer: ", cmd_instance.answer
            self._send_message(self._gen_ans(cmd_instance))
        elif cmd_instance.has_error():
            print " -- cmd_instance.error: ", cmd_instance.error
            self._send_message(self._gen_ans_message2(cmd_name, cmd_instance.cmd_id, "error", cmd_instance.error))

    def _find_command(self, cmd_name):
        print "ALL:", self.__class__.cmd_list['all']
        print "AUTH:", self.__class__.cmd_list['auth']
        if cmd_name in self.__class__.cmd_list['all']:
            print "CMD in ALL"
            return self.__class__.cmd_list['all'][cmd_name]
        print "DJANGOUSER:", self.django_user
        if self.django_user and cmd_name in self.__class__.cmd_list['auth']:
            print "CMD in AUTH"
            return self.__class__.cmd_list['auth'][cmd_name]
        print "CMD not found...."
        return None

    def on_message(self, message):
        """
        Called on client message reception.

        :param message: Message sent by the client.
        :type  message: str.
        :raises: ValueError if misstructured json message.
        """
        print "WebSocketClient.on_message(): self = %s" % self
        print " -- message = %s" % message

        message_deserialized = self._get_valid_cmd_data(message)
        if not message_deserialized:
            self._send_message(self._gen_ack_message("cmd_bad_syntax", None, "error", "Unable to deserialize message."))
        else:
            (message_command, message_data) = message_deserialized
            # if ((message_command not in self.__class__.cmd_list['all']) and
            #     (self.django_user is not None
            #      and message_commnd not in self.__class__.cmd_list['auth'])):
            if not self._find_command(message_command):
                self._send_message(self._gen_ack_message("cmd_unknow", None, "error", "Unknow command <%s>." % message_command))
            else:
                command_id = self._generate_cmd_id(message_command)
                self._process_cmd(message_command, command_id, message_data)

    def on_close(self):
        """
        Delete his own intance of the WebSocketClientManager.
        """
        pass

WebSocketClient.register_cmd(WebSocketEchoCmd)
WebSocketClient.register_cmd(WebSocketUserlistCmd)
## Resto
WebSocketClient.register_cmd(AuthUsersCmd) # Auth user & get profile
WebSocketClient.register_cmd(CreateUserCmd) # Create user
# User Account
WebSocketClient.register_cmd(UpdateUserPasswordCmd, type='auth') # Update user's password
WebSocketClient.register_cmd(GetRestoUsersCmd, type='auth') # Get RestoUser profile
WebSocketClient.register_cmd(UpdateRestoUserCmd, type='auth') # Update user's phone number
# Add friend
WebSocketClient.register_cmd(AddFriendUserCmd, type='auth') # Add friend to list
# Restaurant
WebSocketClient.register_cmd(GetRestaurantCmd, type='auth') # Get restaurant, all or by id
WebSocketClient.register_cmd(UpdateRestaurantCmd, type='auth') # Update restaurant
# Dishe
WebSocketClient.register_cmd(GetDisheCmd, type='auth') # Get dishe by
WebSocketClient.register_cmd(CreateDisheCmd, type='auth') # Add dishe
WebSocketClient.register_cmd(UpdateDisheCmd, type='auth')
WebSocketClient.register_cmd(DeleteDisheCmd, type='auth')
# Reservations
WebSocketClient.register_cmd(GetReservationCmd, type='auth')
WebSocketClient.register_cmd(UpdateReservationCmd, type='auth')
WebSocketClient.register_cmd(CreateReservationCmd, type='auth')
WebSocketClient.register_cmd(DeleteReservationCmd, type='auth')

def start():
    application = tornado.web.Application([
            (r'/ws', WebSocketClient),
            ])
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(8888)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    start()
