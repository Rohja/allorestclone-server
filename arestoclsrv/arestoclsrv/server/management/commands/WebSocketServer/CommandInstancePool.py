#!/usr/bin/env python

from Singleton import SingletonMixin

class CommandInstancePool(SingletonMixin):
    cmdpool = []

    def register_cmd_instance(self, cmdinstance):
        """
        Register a command instance for late processing.

        :param cmdinstance: Instance of WebSocketCmd.
        :type cmdinstance: WebSocketCmd subclass instance.
        """
        print "CommandInstancePool.register_cmd_instance(): self = ", self
        if cmdinstance not in self.cmdpool:
            print " -- cmdinstance: ", cmdinstance
            self.cmdpool.append(cmdinstance)
        else:
            print " -- cmdinstance is already in cmd_pool!"
        print " -- There is actually %d commands in the pool." % len(self.cmdpool)
