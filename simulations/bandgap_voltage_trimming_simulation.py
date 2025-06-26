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
    
    def voltage_measure_callback(self,signal,reference,expected_value):
        self.meter.configure_voltmeter()
        self.meter.set_voltage_dc_nplc(1)
        return False,self.meter.measure_voltage_dc()
    def voltage_trigger_HL_callback(self,signal,reference,threshold,measure_value):
        # Setup trigger on channel 4
        #Level set to 30% of 1.8 V digital signal, falling edge, edge trigger mode
        self.scope.trigger_setup(channel=4, level=1.8 * 0.3, slope='FALL', mode='EDGE')
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
        # configure power supply channel 1 as voltage source 
        if (self.ps.get_emoulation_mode(channel=1) != 'PS1Q') |  (self.ps.get_priority(channel=1) != 'VOLT'):
            self.ps.configure_voltage_source(channel=1,voltage_setpoint=value)
        # set voltage before turn on ......
        self.ps.set_voltage(channel=1,voltage=value)
        # check for the output On status if not turn on 
        if not self.ps.get_outp_state(channel=1) :
            self.ps.output_state(state=True,chan=1)
        return False,float(self.ps.measure_voltage_dc(chan=1))
    
    def generate_clock_callback(self,signal,reference,value):
        self.ps.arb_voltage_sine_generate(channel=1,frequency=value,repeat_count=10e3)
        return False,False


if __name__ == "__main__":
    hwl = HWL()
    # print(g.callback_keys)
    g.hardware_callbacks = {
        'voltage_measure' : hwl.voltage_measure_callback,
        'voltage_force' : hwl.voltage_source,
        'frequency_force' : hwl.generate_clock_callback,
        'voltage_trigger_lh' : hwl.voltage_trigger_LH_callback,
        'voltage_trigger_hl' : hwl.voltage_trigger_HL_callback,
        'frequency_measure' : hwl.frequency_measure_callback
    }
    '''
    Bring 1.2V bandgap reference voltage to IODATA1 through the analog test mux and trim it to the closest value to 1.2V
    '''
    Test_Name = 'BG_1p2V_Trim'
    # Initial value 
    percentage = 1e-2 # 1% deviation

    typical_value = 1.2
    low_value = typical_value - typical_value*percentage
    high_value = typical_value + typical_value*percentage

    buffer_offset = 10e-3 # 10mV
    # Step size (LSB size)
    step_size = 7.57e-3 # 7.57mV

    # Number of steps width of the field / bits
    num_steps = 2^4  # 4-bit

    # Standard deviation for white noise
    noise_std_dev = 0.025

    # Initialize minimum error and optimal code
    min_error = float('inf')
    optimal_code = None
    optimal_measured_value = None

    for i in range(num_steps):
        # sweep trimg code
        # Generate monotonic values with step size
        expected_value = low_value + i * step_size 
        VFORCE(signal='IODATA1', reference='GND', value=expected_value) # use voltage source as bandgap to simulate the bandgap voltage 
        # Add white noise to each value and subtracting the buffer offset
        sleep(0.2) # 1s
        measured_value = VMEASURE(signal='IODATA1', reference='GND', expected_value=expected_value,error_spread=noise_std_dev) - buffer_offset
        error = abs(measured_value - typical_value)/abs(typical_value) *100
        if error < min_error:
            min_error = error
            optimal_code = hex(i)
            optimal_measured_value = measured_value
    hwl.ps.output_state(False,chan=1)
    # Check for limits
    if low_value < optimal_measured_value < high_value:
        print(f'............ {Test_Name} Passed ........')
        # write the optimized code if the trim passed
    else:
        print(f'............ {Test_Name} Failed ........')
        # if the trimh failed program default zero
    print(f"Optimal Code: {optimal_code}")
    print(f"Optimal measured value : {optimal_measured_value}V, Target value : {typical_value}V")

    print(f"Minimum Error: {min_error}%")