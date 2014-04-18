#!/usr/bin/env python

# Python
import json
import time
import md5
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

class WebSocketClient(websocket.WebSocketHandler):
    """
    WebSocketClient represent a user connected to the WebSocket server of Node Manager.
    """
    cmd_list = {} # {"intel": WebSocketIntelCmd, ... }

    def __init__(self, *argv, **kwargs):
        """
        Initialize WebSocketClient.
        """
        print "WebSocketClient.__init__(): self = %s" % self
        super(WebSocketClient, self).__init__(*argv, **kwargs)
        self.__webSocketClientManager = WebSocketClientManager.instance()

    def __unicode__(self):
        return u"%s" % self

    @classmethod
    def register_cmd(cls, cmdclass):
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
        if cmdname in cls.cmd_list:
            print " -- %s already exist in cmd_list." % cmdname
            print " -- cmd_list: ",cls.cmd_list
            return
        print "-- new command (%s, %s)" % (cmdname, cmdclass)
        cls.cmd_list[cmdname] = cmdclass

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

    def open(self):
        """
        Called on client connection.
        Register itself to the WebSocketClientManager instance.
        """
        print "WebSocketClient.open(): self = %s" % self
        self.__webSocketClientManager.add_instance(self)
        self.__webSocketClientManager.get_instance_list()

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
        cmd_instance = self.__class__.cmd_list[cmd_name](cmd_id, cmd_data, self)
        try:
            cmd_instance.filter_data()
        except colander.Invalid, e:
            print " -- Colander error: ", e
            self._send_message(self._gen_ans_message(cmd_instance, "error", "Invalid or missing parameters"))
            return
        cmd_instance.pre_process()
        if cmd_instance.has_answer():
            cmd_instance.need_register = False
            print " -- cmd_instance.answer: ", cmd_instance.answer
            self._send_message(self._gen_ans(cmd_instance))
        if cmd_instance.need_register:
            print " -- Need to register CMD INSTANCE !"

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
            if message_command not in self.__class__.cmd_list:
                self._send_message(self._gen_ack_message("cmd_unknow", None, "error", "Unknow command <%s>." % message_command))
            else:
                command_id = self._generate_cmd_id(message_command)
                self._process_cmd(message_command, command_id, message_data)

    def on_close(self):
        """
        Delete his own intance of the WebSocketClientManager.
        """
        self.__webSocketClientManager.remove_instance(self)

WebSocketClient.register_cmd(WebSocketEchoCmd)

def start():
    application = tornado.web.Application([
            (r'/ws', WebSocketClient),
            ])
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(8888)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    start()
