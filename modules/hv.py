import serial
from ftmlabdaq.protocols import serial

class Board:
    
    def __init__(self, type, port):
        if type=='CAEN':
            self.instrument = serial.Instrument(
                port=port,
                xonxoff = True,
                endl = '\r\n',
                timeout = 0.1
            )
        else: raise KeyError('Unknown board type')

    def get_settings(self):
        return self.instrument.get_settings()

    def send_command(self, command):
        self.instrument.write(command)
        response = self.instrument.read()
        return response
        
    def parse_response(self, response):
        response_list = response.replace('\r\n', '').split(',')
        response_pairs = [s.split(':') for s in response_list]
        response_dict = dict(response_pairs)
        return response_dict

    def read_parameter(self, channel, parameter):
        command = f'$BD:00,CMD:MON,CH:{channel},PAR:{parameter}\r\n'
        response = self.send_command(command)
        response_data = self.parse_response(response)
        return response_data['VAL']

    def set_voltage(self, channel, voltage):
        command = f'$BD:00,CMD:SET,CH:{channel},PAR:VSET,VAL:{voltage}\r\n'
        self.instrument.write(command)
    
    def get_vset(self, channel):
        return float(self.read_parameter(channel, 'VSET'))
    
    def get_vmon(self, channel):
        return float(self.read_parameter(channel, 'VMON'))