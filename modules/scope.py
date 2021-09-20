import numpy
import vxi11

class ScopeLecroy:

    def __init__(self, hostname):
        self.hostname = hostname
        self.scope = scope = vxi11.Instrument(hostname)

        print('Initializing communication to scope...')
        self.scope.write('TRMD?')
        print('Trigger', self.scope.read())

    