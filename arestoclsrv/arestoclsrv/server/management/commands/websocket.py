from django.core.management.base import BaseCommand, CommandError
from WebSocketServer.WebSocketClient import start

class Command(BaseCommand):
    args = ''
    help = 'Run websocket server'

    def handle(self, *args, **options):
        start()
        # raise CommandError('Poll "%s" does not exist' % poll_id)
        # self.stdout.write('Successfully closed poll "%s"' % poll_id)
        
