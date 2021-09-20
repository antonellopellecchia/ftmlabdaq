import requests

class Attenuator:

    def __init__(self, hostname, port):
        self.hostname = hostname
        self.port = port
        self.protocol = 'http://'
        self.request_url = f'{self.protocol}{self.hostname}:{self.port}'

    def get_attenuation(self):
        url_get = f'{self.request_url}/get'
        response = requests.get(url_get)
        response_data = response.json()
        
        if response_data['status']=='OK': return float(response_data['attenuation'])
        else: raise ConnectionError('Error getting attenuation')

    def set_attenuation(self, attenuation):
        url_set = f'{self.request_url}/set/{attenuation}'
        response = requests.get(url_set)
        response_data = response.json()
        
        if response_data['status']!='OK':
            raise ConnectionError('Error setting attenuation')