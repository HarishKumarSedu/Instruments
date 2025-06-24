from Instruments import DPO4054
from time import sleep

osc = DPO4054('USB0::0x0699::0x0401::C020132::INSTR')

# osc.set_channel_display(channel=1,display=False)
# osc.set_timebase_scale(1/(2*125)) # 125H Input signal
# osc.setup_channel(channel=3,label='clk',display=True,scale=1,position=0.0,offset=0.0,coupling='DC',bandwidth='FULL',invert=False)
# osc.trigger_setup(channel=3,level=1.8*0.9,slope='RISE',mode='EDGE') # level set for digital sinal 
# # osc.add_measurement(channel=3,meas_type='FREQ',slot=1,source=1)
# osc.add_immediate_measurement(channel=3,meas_type='FREQ',source=1) # FREQ measurement
# osc.single_sequence(timeout=20,sampling_interval=1e-6)
# sleep(1) # wait for the scope to acquire data
# print(f'FREQ immediate : { osc.get_immediate_measurement()}') # FREQ measurement
# # print(f'FREQ : { osc.get_measurement(channel=3,slot=1,source=1)}') # FREQ measurement

## .................... Simulate continuous acquisition and Trigger ....................
# gose into normal and sequenctial acquire mode 
osc.setup_channel(channel=3,label='clk',display=True,scale=100e-3,position=0.0,offset=0.0,coupling='AC',bandwidth='FULL',invert=False)
osc.trigger_setup(channel=3,level=80e-3,slope='RISE',mode='EDGE') # analog sinusoidal signal 1V @ac signal 100mV, trigger level at 90%
osc.add_measurement(channel=3,meas_type='FREQ',slot=1,source=1)
osc.set_acquire_sequence() # Set the oscilloscope to sequence mode
volt = 0 
while volt < 3.3:   # Simulate a voltage increase
    if osc.get_operation_status():
        sleep(0.5)  # wait for the scope to acquire data
        print(f'FREQ immediate : { osc.get_measurement(channel=3,slot=1,source=1)}') # FREQ measurement
        break
    volt+= 0.1  # Simulate a voltage increase
    
# # release the scope in freeze mode 
osc.set_acquire_continuous() # let scopr run freely
# osc.close()