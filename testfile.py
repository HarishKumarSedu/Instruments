from Instruments import DPO4054
osc = DPO4054('USB0::0x0699::0x0401::C020132::INSTR')
# Example usage:
osc.set_timebase_scale(2/(5e3))
osc.setup_channel(3, display=True, scale=0.1, position=0.0, coupling='AC', bandwidth_limit='20MHz')  # Sets up CH1
osc.setup_edge_trigger(source_channel=3,level=50e-3,slope='RISE')  # Sets up edge trigger on CH3
osc.add_measurement('FREQ', 3,1)           # Adds frequency measurement on CH1
import time
time.sleep(2)  # Wait for the oscilloscope to process the commands
print(osc.get_measurement( 3,1))  # Get the measurement value for CH1
