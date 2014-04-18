#!/usr/bin/env python

import colander

LOGS_TYPE = ['error', 'warning', 'info', 'debug']
THREADS_CMD = ['start', 'stop', 'status']

### COMMAND ###
class WebSocketCmdScheme(colander.MappingSchema):
    cmd = colander.SchemaNode(colander.String())

class WebSocketThreadCmdScheme(WebSocketCmdScheme):
    id = colander.SchemaNode(colander.String())
    process = colander.SchemaNode(colander.String(),
                                  validator=colander.OneOf(THREADS_CMD))

