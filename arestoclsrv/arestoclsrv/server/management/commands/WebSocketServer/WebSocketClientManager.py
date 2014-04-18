#!/usr/bin/env python

import time

from Singleton import SingletonMixin

class WebSocketClientManager(SingletonMixin):
    """WebSocketClientManager is used for manage all WebSocketClient instance."""
    # FIXME: Error handling
    #        Real design
    instance_list = []

    def __init__(self):
        print "WebSocketClientManager.__init__(): self = %s" % self

    def remove_instance(self, instance):
        """
        Remove a WebSocketClient instance from the instance list.
        
        :param instance: WebSocketClient instance.
        :type  instance: WebSocketClient.
        """
        print "WebSocketClientManager.remove_instance(): self = %s" % self
        print " -- instance: %s" % instance
        # FIXME: New way to check (now use dict).
        if instance not in self.instance_list:
            print " -- instance not found !"
        self.instance_list = filter(lambda a: a['object'] != instance, self.instance_list)
        
    def add_instance(self, instance):
        """
        Add a WebSocketClient instance on instance list.
        
        :param instance: WebSocketClient instance.
        :type  instance: WebSocketClient.
        """
        print "WebSocketClientManager.add_instance(): self = %s" % self
        print " -- instance: ", instance
        if instance not in self.instance_list:
            instance_data = {'ip': instance.ws_connection.request.remote_ip,
                             'object': instance,
                             'connection_timestamp': time.time(),
                             'lastcmd_timestamp': None}
            self.instance_list.append(instance_data)
        else:
            print " -- instance already in list!"

    def get_instance_list(self):
        """
        Get the instance list.
        
        :return: The list containing all the WebSocketClient instance.
        :rtype: list.
        """
        print "WebSocketClientManager.get_instance_list(): self = %s" % self
        print " -- instance_list:"
        for instance in self.instance_list:
            print " -- [IP: ", instance['ip'].rjust(16,' '), "Instance: ", instance['object'], "]"
            print " -- [[ Connection: ", instance['connection_timestamp'], " Last command: ", instance['lastcmd_timestamp'], ']]'
        return self.instance_list
