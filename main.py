from Instruments.a34461 import A34461
from Instruments.dpo4054 import DPO4054
from Instruments.n67xx import N67xx
from PyMCP2221A import PyMCP2221A
from time import sleep 
from dfttools import *
from dfttools import g
import random
import math 

# meter = A34461('USB0::0x2A8D::0x1401::MY57200246::INSTR')

class HWL:
    def __init__(self):
        try:
            self.mcp = PyMCP2221A.PyMCP2221A()
            self.mcp.I2C_Init()
            print("I2C bridge initialized")
        except Exception as e:
            print(f"I2C bridge init failed: {e}")
            self.mcp = None
        try:
            from Instruments.a34461 import A34461
            self.meter = A34461('USB0::0x2A8D::0x1401::MY57200246::INSTR')
        except Exception:
            print("Meter not found or connection failed")
            self.meter = None

        try:
            from Instruments.n67xx import N67xx
            self.ps = N67xx('USB0::0x0957::0x0F07::MY50002157::INSTR')
        except Exception:
            print("Power supply not found or connection failed")
            self.ps = None

        try:
            from Instruments.dpo4054 import DPO4054
            self.scope = DPO4054('USB0::0x0699::0x0401::C020132::INSTR')
            # Example of scope setup if connected
            self.scope.setup_channel(channel=4, label='uvlo', display=True, scale=1)
            self.scope.set_channel_display(channel=1, display=False)
            self.scope.set_acquire_continuous()
        except Exception:
            print("Scope not found or connection failed")
            self.scope = None
        '''
            # setup digital sope for comparator detect 
            
        '''

    # -------------------
    # I2C Callback Functions
    
    def i2c_reg_write(self, device_address: int, register_address: int, value: int) -> bool:
        """Write a value to an I2C register using the MCP bridge."""
        if self.mcp is None:
            print("I2C bridge not available")
            return False
        try:
            # Compose data to write: register address + value
            data = bytearray([register_address, value & 0xFF])
            self.mcp.I2C_Write(device_address, data)
            print(f"[i2c_reg_write] Wrote 0x{value:X} to dev 0x{device_address:X}, reg 0x{register_address:X}")
            return True
        except Exception as e:
            print(f"I2C reg write error: {e}")
            return False

    def i2c_reg_read(self, device_address: int, register_address: int, No_bytes: int = 1) -> int:
        """Read a value from an I2C register using the MCP bridge."""
        if self.mcp is None:
            print("I2C bridge not available")
            return 0
        try:
            # Write register address first
            self.mcp.I2C_Write(device_address, bytearray([register_address]))
            # Then read bytes from that register
            read_data = self.mcp.I2C_Read(device_address, No_bytes)
            if len(read_data) > 0:
                value = read_data[0]
                print(f"[i2c_reg_read] Read 0x{value:X} from dev 0x{device_address:X}, reg 0x{register_address:X}")
                return value
            else:
                print("I2C read returned empty data")
                return 0
        except Exception as e:
            print(f"I2C reg read error: {e}")
            return 0

    def i2c_bit_write(self, device_address: int, register_address: int, msb: int, lsb: int, value: int) -> bool:
        """Write bits to an I2C register using the MCP bridge."""
        # This example assumes full byte write; bit masking can be added if needed.
        return self.i2c_reg_write(device_address, register_address, value)

    def i2c_bit_read(self, device_address: int, register_address: int, msb: int, lsb: int, expected_value: int = None):
        """Read bits from an I2C register using the MCP bridge."""
        # This example just reads the full register value.
        return self.i2c_reg_read(device_address, register_address, No_bytes=1)

    
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
    
    def current_source(self,signal,reference,value):
        # configure power supply channel 3 as voltage source 
        if (self.ps.get_emoulation_mode(channel=3) != 'PS2Q') |  (self.ps.get_priority(channel=3) != 'CURR'):
            self.ps.configure_current_sink_source(channel=3,current_setpoint=value)
        # set voltage before turn on ......
        self.ps.set_current(channel=3,current=value)
        # check for the output On status if not turn on 
        if not self.ps.get_outp_state(channel=3) :
            self.ps.output_state(state=True,chan=3)
        return False,float(self.ps.measure_voltage_dc(chan=3))
    
    def generate_clock_callback(self,signal,reference,value):
        self.ps.arb_voltage_sine_generate(channel=1,frequency=value,repeat_count=10e3)
        return False,False
    
    def current_load(self,value):
        self.ps.configure_CC_load(channel=1)
        if not self.ps.get_outp_state(channel=1) :
            self.ps.output_state(state=True,chan=1)
        self.ps.set_current(channel=1,current=value)
        return self.ps.measure_voltage_dc(chan=1)


if __name__ == "__main__":
    hwl = HWL()
    # print(g.callback_keys)
    g.hardware_callbacks = {
        'voltage_measure' : hwl.voltage_measure_callback,
        'voltage_force' : hwl.voltage_source,
        'current_force' : hwl.current_source,
        'frequency_force' : hwl.generate_clock_callback,
        'voltage_trigger_lh' : hwl.voltage_trigger_LH_callback,
        'voltage_trigger_hl' : hwl.voltage_trigger_HL_callback,
        'frequency_measure' : hwl.frequency_measure_callback
    }
    Test_Name = 'High_side_P_Ron'
    # Wait for device stabilization

    I_forced= -0.5

    # Step 3: Force 500mA current into OUTP pin
    current = AFORCE(signal='OUTP', reference='PGND', value=I_forced, error_spread=0.05)  # 500mA ±5%
    sleep(1)  # 1 µs
    dv1 = hwl.current_load(value=I_forced) # simulate load ....
    dV = VMEASURE(signal='PVDD', reference='OUTN', expected_value=0.062, error_spread=0.01) #pin 10
    LSN_ron = abs(dV / I_forced) - 0.025 # R = V/I
    print(f'Calculated highside P-Ron: {LSN_ron:.3f} Ohms')
    print(f'[Expected ~100m Ohms typical, based on dV={dV:.3f}V @ {I_forced*1000:.0f}mA]')
    hwl.ps.output_state(state=False,chan=3)
    hwl.ps.output_state(state=False,chan=1)