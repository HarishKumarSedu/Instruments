
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
        self.scope.set_timebase_scale(1 / (2 * 1E6)) # Input signal frequency: 1M Hz
    
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

    def voltage_source(self,signal,reference,value):

        self.ps.set_voltage(channel=1,voltage=value)
        self.ps.output_state(state=True,chan=1)
        return False,float(self.ps.measure_voltage_dc(chan=1))


if __name__ == "__main__":
    hwl = HWL()
    g.hardware_callbacks = {
        # 'voltage_measure' : hwl.voltmeter_callback,
        # 'voltage_force' : hwl.voltage_source,
        'voltage_trigger_lh' : hwl.voltage_trigger_LH_callback
    }

    LH_Th = 2.25  # 2.25V threshold
    error_spread = LH_Th*0.1 # 10% error spread
    code_width = 5  # 5 bits trimming code
    min_error = float('inf')
    optimal_code = None
    optimal_measured_value = None
    force_voltage_low_limit = 2  # minimum voltage limit
    force_voltage_high_limit = 3  # maximum voltage limit

    for Code in range(2^code_width):
        # TODO: Write trimming code to device via I2C
        # Example (uncomment and fill device_address and field_info):
        force_voltage = force_voltage_low_limit
        trigger = False

        while True:
            # Add noise simulation
            pvdd_forced_voltage = VFORCE(signal='PVDD', reference='GND', value=force_voltage,error_spread=error_spread)
            # Check trigger condition
            trigger = VTRIG_LH(signal='IODATA0', reference='GND', threshold=LH_Th, expected_value=force_voltage)

            if trigger:
                break
            elif pvdd_forced_voltage >= force_voltage_high_limit:
                print(f'..... Voltage max limit {force_voltage_high_limit}V crossed ........')
                break

            force_voltage += 0.01  # decrease voltage by 10mV
            sleep(0.001)  # 1 ms delay

        error = abs(pvdd_forced_voltage - LH_Th)/abs(LH_Th) * 100
        if error < min_error:
            min_error = error
            optimal_code = hex(Code)
            optimal_measured_value = pvdd_forced_voltage

    # Final check and reporting
    if force_voltage_low_limit < optimal_measured_value < force_voltage_high_limit:
        print(f'............ UVLO_Trim Test Passed ........')
        # # TODO: Burn optimal trimming code to OTP via I2C
        # I2C_WRITE(device_address=DEVICEADDR, field_info=otp_ds_ref_pvdd_uvlo_trm, write_value=optimal_code)
    else:
        print(f'............ UVLO_Trim Test Failed ........')
        # I2C_WRITE(device_address=DEVICEADDR, field_info=otp_ds_ref_pvdd_uvlo_trm, write_value=0x0)

    print(f"Optimal Code: {optimal_code}")
    print(f"Optimal Measured Value: {optimal_measured_value:.4f} V (Target: {LH_Th} V)")
    print(f"Minimum Error: {min_error:.6f} %")