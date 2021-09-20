#!/usr/bin/python3

import numpy as np
import vxi11
import matplotlib.pyplot as plt

scope = vxi11.Instrument('192.167.91.242')

scope.write('TRMD?')
print('Trigger', scope.read())

scope.write('TRMD AUTO')
scope.write('TRMD?')
print('Trigger', scope.read())

scope.write('TRMD?')
print('Trigger', scope.read())

scope.write('CHDR OFF')
scope.write('INR?')
print('New signal acquired? ', scope.read())

scope.write("WFSU SP, 1, NP, 0, FP, 0, SN, 0")

print('Getting header...')
scope.write("C2:INSP? 'WAVEDESC'")
header = scope.read()
print(header)

print('Getting waveform...')
scope.write('C2:WF?')
msg = scope.read_raw()
print('Size', len(msg))

start = msg.find(b'WAVEDESC')
msg = msg[start:]

# extract the number of elements in the binary data
nb_byte_1 = np.fromstring(msg[60:64], dtype=np.uint32)
nb_byte_2 = np.fromstring(msg[64:68], dtype=np.uint32)
n_start = np.fromstring(msg[124:128], dtype=np.uint32)
n_first = np.fromstring(msg[132:136], dtype=np.uint32)
n_end = np.fromstring(msg[128:132], dtype=np.uint32)
n_sparse = np.fromstring(msg[136:140], dtype=np.uint32)

print(nb_byte_1, nb_byte_2)

# check the number of elements
assert nb_byte_2 == 0, "invalid array"
assert n_start == 0, "invalid array"
assert n_first == 0, "invalid array"
assert (nb_byte_1 % 2) == 0, "invalid array"
assert (nb_byte_1 / 2) == np.floor(n_end / n_sparse) + 1, "invalid array"

# extract the scaling and offset information
nb = int(nb_byte_1 / 2)
v_gain = np.fromstring(msg[156:160], dtype=np.float32)
v_offset = np.fromstring(msg[160:164], dtype=np.float32)
t_gain = np.fromstring(msg[176:180], dtype=np.float32)
t_offset = np.fromstring(msg[180:188], dtype=np.float64)

# extract the waveform data, scale, and offset
v = np.fromstring(msg[346:], dtype=np.int16, count=nb).astype(np.float)
v *= v_gain
v -= v_offset

# extract the time data, scale, and offset
t = np.arange(nb, dtype=np.float)
t += t_offset

# return the data
print(nb)

fig = plt.figure()
plt.plot(t, v)
fig.savefig('waveform.png')