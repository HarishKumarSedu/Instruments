import time
import pyvisa as visa

class RP790x:
    def __init__(self, port='GPIB0::7::INSTR'):
        self.rm = visa.ResourceManager()
        self.my_instr = self.rm.open_resource(port)
        self.my_instr.read_termination = '\n'
        self.my_instr.write_termination = '\n'
        print(f"Connected to: {self.get_idn()}")

    # Identification
    def get_idn(self):
        return self.my_instr.query('*IDN?').strip()

    # Output Control
    def output_on(self):
        self.my_instr.write('OUTP ON')
        print("Output turned ON")

    def output_off(self):
        self.my_instr.write('OUTP OFF')
        print("Output turned OFF")

    def output_status(self):
        status = self.my_instr.query('OUTP?').strip()
        print(f"Output status: {status}")
        return status

    # Function Priority
    def set_current_priority(self):
        self.my_instr.write('FUNC CURR')
        print("Set function priority to CURRENT")

    def set_voltage_priority(self):
        self.my_instr.write('FUNC VOLT')
        print("Set function priority to VOLTAGE")

    # Set Limits and Setpoints
    def set_current_limit(self, current):
        if current >= 0:
            self.my_instr.write(f'CURR:LIM {current}')
            print(f"Set positive current limit: {current} A")
        else:
            self.my_instr.write(f'CURR:LIM:NEG {abs(current)}')
            print(f"Set negative current limit: {abs(current)} A")

    def set_voltage_limit_high(self, voltage):
        self.my_instr.write(f'VOLT:LIM {voltage}')
        print(f"Set voltage high limit: {voltage} V")

    def set_voltage_limit_low(self, voltage):
        self.my_instr.write(f'VOLT:LIM:LOW {voltage}')
        print(f"Set voltage low limit: {voltage} V")

    def set_voltage(self, voltage):
        self.my_instr.write(f'VOLT {voltage}')
        print(f"Set voltage: {voltage} V")

    def set_current(self, current):
        self.my_instr.write(f'CURR {current}')
        print(f"Set current: {current} A")

    # Measurements
    def measure_voltage(self):
        val = float(self.my_instr.query('MEASure:VOLTage?'))
        print(f"Measured voltage: {val} V")
        return val

    def measure_current(self):
        val = float(self.my_instr.query('MEASure:CURR?'))
        print(f"Measured current: {val} A")
        return val

    def measure_power(self):
        val = float(self.my_instr.query('MEASure:POW?'))
        print(f"Measured power: {val} W")
        return val

    # Protection Settings
    def set_over_voltage_protection(self, voltage):
        self.my_instr.write(f'VOLT:PROT {voltage}')
        print(f"Set over-voltage protection: {voltage} V")

    def set_over_current_protection(self, current):
        self.my_instr.write(f'CURR:PROT {current}')
        print(f"Set over-current protection: {current} A")

    def enable_over_current_protection(self):
        self.my_instr.write('CURR:PROT:STAT ON')
        print("Enabled over-current protection")

    def disable_over_current_protection(self):
        self.my_instr.write('CURR:PROT:STAT OFF')
        print("Disabled over-current protection")

    def clear_protection(self):
        self.my_instr.write('OUTP:PROT:CLE')
        print("Cleared protection status")

    # Output Delay Control
    def set_rise_delay(self, delay_s):
        self.my_instr.write(f'OUTP:DEL:RISE {delay_s}')
        print(f"Set output rise delay: {delay_s} s")

    def set_fall_delay(self, delay_s):
        self.my_instr.write(f'OUTP:DEL:FALL {delay_s}')
        print(f"Set output fall delay: {delay_s} s")

    # Channel Grouping
    def couple_channels(self, channels):
        ch_str = ','.join(f'CH{ch}' for ch in channels)
        self.my_instr.write(f'OUTP:COUP:CHAN {ch_str}')
        print(f"Coupled channels: {ch_str}")

    def set_series_mode(self):
        self.my_instr.write('OUT:PAIR SER')
        print("Set output mode: SERIES")

    def set_parallel_mode(self):
        self.my_instr.write('OUT:PAIR PAR')
        print("Set output mode: PARALLEL")

    # Utility Functions
    def wait_for_voltage_stabilization(self, channel: int, target_voltage: float, tolerance=0.01, timeout=10):
        print(f"Waiting for voltage stabilization at {target_voltage} V ±{tolerance} V")
        start_time = time.time()
        while time.time() - start_time < timeout:
            voltage = self.measure_voltage()
            if abs(voltage - target_voltage) <= tolerance:
                print("Voltage stabilized")
                return True
            time.sleep(0.1)
        print("Voltage stabilization timeout")
        return False

    def ramp_voltage(self, channel: int, start_v: float, stop_v: float, step_v: float, delay_s=0.1):
        print(f"Ramping voltage from {start_v} V to {stop_v} V in steps of {step_v} V")
        voltage = start_v
        step = abs(step_v) if stop_v > start_v else -abs(step_v)
        while (voltage <= stop_v if step > 0 else voltage >= stop_v):
            self.set_voltage(voltage)
            time.sleep(delay_s)
            voltage += step
        self.set_voltage(stop_v)
        print("Voltage ramp complete")

    # Application-level voltage sweep test
    def voltage_sweep_test(self, channel: int, start_v: float, stop_v: float, step_v: float, current_limit: float):
        print(f"Voltage sweep on channel {channel} from {start_v} V to {stop_v} V")
        self.set_current(current_limit)
        self.output_on()
        results = []
        voltage = start_v
        while voltage <= stop_v:
            self.set_voltage(voltage)
            if not self.wait_for_voltage_stabilization(channel, voltage):
                print(f"Warning: Voltage did not stabilize at {voltage} V")
            meas_v = self.measure_voltage()
            meas_i = self.measure_current()
            print(f"Set V: {voltage:.3f} V, Meas V: {meas_v:.3f} V, Meas I: {meas_i:.3f} A")
            results.append({'Set_Voltage': voltage, 'Measured_Voltage': meas_v, 'Measured_Current': meas_i})
            voltage += step_v
        self.output_off()
        return results

    # Close connection
    def close(self):
        self.my_instr.close()
        print("Connection closed")


# Example usage
if __name__ == '__main__':
    supply = RP790x(port='GPIB0::7::INSTR')
    print(supply.get_idn())

    supply.set_current_limit(1.5)
    supply.set_voltage_limit_high(5.5)
    supply.set_voltage(5)
    supply.output_on()
    time.sleep(1)

    print(f"Voltage: {supply.measure_voltage():.3f} V")
    print(f"Current: {supply.measure_current():.3f} A")
    print(f"Power: {supply.measure_power():.3f} W")

    sweep_results = supply.voltage_sweep_test(channel=1, start_v=3.0, stop_v=5.0, step_v=0.5, current_limit=1.0)
    for r in sweep_results:
        print(r)

    supply.output_off()
    supply.close()
