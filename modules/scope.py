import vxi11
import numpy as np
import matplotlib.pyplot as plt

class ScopeLecroy:

    def __init__(self, hostname):
        self.hostname = hostname
        self.scope = vxi11.Instrument(hostname)

        print('Initializing communication to scope...')
        self.scope.write('TRMD?')
        print('Trigger', self.scope.read())

    def configure(self):
        # prepare scope for waveform acquisition and transfer
        self.scope.write("WFSU SP, 1, NP, 0, FP, 0, SN, 0")

    @property
    def trigger_mode(self):
        self.scope.write('TRMD?')
        return self.scope.read()

    @trigger_mode.setter
    def trigger_mode(self, mode):
        self.scope.write(f'TRMD {mode}')
        if not self.trigger_mode==mode:
            raise ConnectionError('Error setting trigger mode')
    
    @property
    def triggered(self):
        # tells whether the scope has triggered since the last poll
        self.scope.write('CHDR OFF')
        self.scope.write('INR?')
        has_triggered = self.scope.read()
        return has_triggered!='0'

    def set_threshold(self, channel, threshold, edge='NEG'):
        # set trigger slope, channel and threshold in mV
        self.scope.write(f'TRSL {edge}')
        self.scope.write(f'TRIG_SELECT EDGE,SR,{channel}')
        self.scope.write(f'{channel}:TRIG_LEVEL {threshold} mV')

    def get_waveform_raw(self, channel):
        # gets last triggered waveform from chosen channel
        self.scope.write(f'{channel}:WF?')
        return self.scope.read_raw()
    
    def get_waveform(self, channel):
        scope_response = self.get_waveform_raw(channel)
        return Waveform.unpack(scope_response, format='IEEE488.2')

class Waveform:

    def __init__(self, x, y):
        self.x, self.y = x, y

    def unpack(packet, format):
        if format=='IEEE488.2':
            """Unpack scope standard waveform"""

            # apply offset to response packet
            start = packet.find(b'WAVEDESC')
            packet = packet[start:]

            packet_length = np.frombuffer(packet[60:64], dtype=np.uint32)
            wf_length = int(packet_length/2)
            x = np.arange(wf_length, dtype=np.float64)
            y = np.frombuffer(packet[346:], dtype=np.int16, count=wf_length).astype(np.float64)

            x_gain = np.frombuffer(packet[176:180], dtype=np.float32)
            x_offset = np.frombuffer(packet[180:188], dtype=np.float64)
            x *= x_gain
            x += x_offset
            x *= 1e9

            y_gain = np.frombuffer(packet[156:160], dtype=np.float32)
            y_offset = np.frombuffer(packet[160:164], dtype=np.float32)
            y *= y_gain
            y -= y_offset

            waveform = Waveform(x, y)
            return waveform
        else: raise ValueError('Unrecognized waveform packet format')
    
    def __len__(self):
        return self.x.size

    def __add__(self, offset):
        result_wf = Waveform(self.x, self.y+offset)
        return result_wf

    def __sub__(self, offset):
        return self + (-offset)

    @property
    def min(self):
        return min(self.y)

    @property
    def max(self):
        return max(self.y)

    @property
    def baseline(self):
        baseline_stop = int(0.3*len(self))
        baseline_points = self.y[:baseline_stop]
        return baseline_points.mean()

    @property
    def charge(self):
        return sum(self.y)*(self.x[1]-self.x[0])/50

    def subtract_baseline(self):
        return self - self.baseline

    def save_figure(self, figure_path):
        fig = plt.figure()
        plt.plot(self.x, self.y)
        plt.xlabel('Time (ns)')
        plt.ylabel('Voltage (mV)')
        fig.savefig(figure_path)
