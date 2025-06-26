from Instruments.a34461 import A34461
from Instruments.dpo4054 import DPO4054
from Instruments.n67xx import N67xx
from time import sleep 
from dfttools import *
from dfttools import g
import random
import math 

# meter = A34461('USB0::0x2A8D::0x1401::MY57200246::INSTR')
class HWL:

    def __init__(self):
        self.meter = A34461('USB0::0x2A8D::0x1401::MY57200246::INSTR')
        self.ps = N67xx('USB0::0x0957::0x0F07::MY50002157::INSTR')
        self.scope = DPO4054('USB0::0x0699::0x0401::C020132::INSTR')

        '''
            # setup digital sope for comparator detect 
            
        '''

        # Configure channel 4:
        # Label as 'uvlo', enable display, 1 V/div scale, 0 position, 0 offset,
        # DC coupling, full bandwidth, no inversion
        self.scope.setup_channel(channel=4,label='uvlo',display=True,scale=1,position=0.0,offset=0.0,coupling='DC',bandwidth='FULL',invert=False)
        self.scope.set_channel_display(channel=1, display=False)
        # Set timebase scale to half the input signal frequency (1M Hz)
        self.scope.set_acquire_continuous()
    
    def voltage_trigger_LH_callback(self,signal,reference,threshold,measure_value):
        # Setup trigger on channel 4
        #Level set to 90% of 1.8 V digital signal, rising edge, edge trigger mode
        self.scope.trigger_setup(channel=4, level=1.8 * 0.9, slope='RISE', mode='EDGE')
        self.scope.set_acquire_sequence() # set scope in normal to do acquire 
        #-----------------------------------------------------------
        ## this snippet is for similation purpose 
        ## This is taken care by device comparator to generate the digital signal
        #-----------------------------------------------------------
        '''
            # Setup power supply channel 1 as digital signal generate 
            for simulation purpose to see the comparator trigger in the scope
        '''
        self.ps.configure_voltage_source(channel=1) # configure supply channel 1 as digital signal generator 
        self.ps.output_state(state=True,chan=1) # turn on power supply
        if math.isclose(threshold, measure_value, rel_tol=0.08): # 5% check threshold vlaue and measured value close to 5%
            self.ps.set_voltage(channel=1,voltage=1.8) # generate digital thrigger signal
        else:
            self.ps.set_voltage(channel=1,voltage=0)
        # see wheather it is triggered
        if self.scope.get_operation_status(): # code staty it is not simulation code / check the comparator triggered
            self.ps.set_voltage(channel=1,voltage=0) # comparator simulation code 
            self.ps.output_state(state=False,chan=1) # comparator simulation code turn off
            return True,True
        self.ps.set_voltage(channel=1,voltage=0) # comparator simulation code 
        self.ps.output_state(state=False,chan=1) # comparator simulation code turn off
        return True,False
    
    def voltmeter_callback(self,*args,**kwargs):
        print(args,kwargs)
        return False,False
    def frequency_measure_callback(self,signal,reference,expected_value):
        # self.scope.add_measurement('AMP', 4, 1) # add signal amplitude in the 
        # #Level set to 50% of 1.8 V analog  signal, rising edge, edge trigger mode
        if expected_value:
            self.scope.set_timebase_scale(1 / (2 * expected_value)) # set time base : expected_frequency Hz
        self.scope.add_measurement(channel=4,meas_type='AMPL',slot=1,source=1) # signal amplitude measure in slot1,source 1
        self.scope.add_measurement(channel=4,meas_type='FREQ',slot=2,source=1) # signal amplitude measure in slot1,source 1
        sleep(1)
        signal_amplitude = self.scope.get_measurement(channel=4,slot=1,source=1)
        self.scope.trigger_setup(channel=4, level=signal_amplitude * 0.5, slope='RISE', mode='EDGE') # analog singnal set level half of the singnal
        measures = 5
        Freq = 0
        for _ in range(measures):
            Freq += self.scope.get_measurement(channel=4,slot=2,source=1)
            sleep(0.1)
        Freq = Freq/measures
        return True,Freq
    
    def voltage_source(self,signal,reference,value):
        self.ps.set_voltage(channel=1,voltage=value)
        self.ps.output_state(state=True,chan=1)
        return False,float(self.ps.measure_voltage_dc(chan=1))
    
    def generate_clock_callback(self,signal,reference,value):
        self.ps.arb_voltage_sine_generate(channel=1,frequency=value,repeat_count=10e3)
        return False,False


if __name__ == "__main__":
    hwl = HWL()
    print(g.callback_keys)
    g.hardware_callbacks = {
        'voltage_measure' : hwl.voltmeter_callback,
        # 'voltage_force' : hwl.voltage_source,
        'frequency_force' : hwl.generate_clock_callback,
        'voltage_trigger_lh' : hwl.voltage_trigger_LH_callback,
        'frequency_measure' : hwl.frequency_measure_callback
    }
    target_value = 1e3          # 1KHz
    lower_limit = 0.9e3 
    higher_limit = 1.1e3
    # Initialize minimum error and optimal code
    min_error = float('inf')
    optimal_code = None
    optimal_measured_value = None
    num_steps = 2**4  # trimming field is 2 bit
    step_size = 40

    for i in range(num_steps):
        expected_value =lower_limit + step_size*(i+1)   
        FREQFORCE(signal='IODATA1', reference='GND',value=expected_value) # generate signal                                                           # wait 100us
        sleep(1)       
        measured_value = FREQMEASURE(signal='IODATA1', reference='GND',expected_value=expected_value)                     # Measure Frequency at IODATA1
        error = abs(measured_value - target_value)                                      # Calculate the distance from the target 1KHz
    
        # Check if the measured value is the nearest to the target   
        if error < min_error:
            min_error = error
            optimal_code = hex(i)
            optimal_measured_value = measured_value
    
    
print(f"Optimal Code: {optimal_code}")
print(f"Optimal measured value : {optimal_measured_value}Hz, Target vlaue : {target_value}Hz")
print(f"Minimum Error: {min_error}%")