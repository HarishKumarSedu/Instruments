import time
import pyvisa as visa

class E362X:
    def __init__(self, port='GPIB0::7::INSTR'):
        self.rm = visa.ResourceManager()
        self.supply = self.rm.open_resource(port)
        self.supply.read_termination = '\n'
        self.supply.write_termination = '\n'

    # Identification
    def get_idn(self):
        return self.supply.query('*IDN?').strip()

    # Output Control
    def output_on(self, channel: int):
        self.supply.write(f'OUTP ON,(@{channel})')

    def output_off(self, channel: int):
        self.supply.write(f'OUTP OFF,(@{channel})')

    def output_status(self, channel: int):
        return self.supply.query(f'OUTP? (@{channel})').strip()

    # Voltage and Current Setting
    def set_voltage(self, channel: int, voltage):
        self.supply.write(f'VOLT {float(voltage)},(@{channel})')

    def set_current(self, channel: int, current):
        self.supply.write(f'CURR {float(current)},(@{channel})')

    # Measurements
    def measure_voltage(self, channel: int):
        return float(self.supply.query(f'MEAS:VOLT? (@{channel})'))

    def measure_current(self, channel: int):
        return float(self.supply.query(f'MEAS:CURR? (@{channel})'))

    # 4-Wire Remote Sense Control
    def enable_4wire_sense(self, channel: int):
        """
        Enables 4-wire remote sensing on the specified channel.
        SCPI command example: 'SYST:RSEN ON, (@channel)'
        """
        self.supply.write(f'SYST:RSEN ON,(@{channel})')

    def disable_4wire_sense(self, channel: int):
        """
        Disables 4-wire remote sensing on the specified channel.
        SCPI command example: 'SYST:RSEN OFF, (@channel)'
        """
        self.supply.write(f'SYST:RSEN OFF,(@{channel})')

    def query_4wire_sense_status(self, channel: int):
        """
        Queries the 4-wire remote sensing status for the specified channel.
        Returns 'ON' or 'OFF'.
        """
        resp = self.supply.query(f'SYST:RSEN? (@{channel})').strip()
        return resp

    # Protection Settings
    def set_over_voltage_protection(self, channel: int, voltage):
        self.supply.write(f'VOLT:PROT {float(voltage)},(@{channel})')

    def set_over_current_protection(self, channel: int, current):
        self.supply.write(f'CURR:PROT {float(current)},(@{channel})')

    def enable_over_current_protection(self, channel: int):
        self.supply.write(f'CURR:PROT:STAT ON,(@{channel})')

    def disable_over_current_protection(self, channel: int):
        self.supply.write(f'CURR:PROT:STAT OFF,(@{channel})')

    def clear_protection(self, channel: int):
        self.supply.write(f'OUTP:PROT:CLE (@{channel})')

    # Utility Methods
    def wait_for_voltage_stabilization(self, channel: int, target_voltage: float, tolerance=0.01, timeout=10):
        start_time = time.time()
        while time.time() - start_time < timeout:
            voltage = self.measure_voltage(channel)
            if abs(voltage - target_voltage) <= tolerance:
                return True
            time.sleep(0.1)
        return False

    def ramp_voltage(self, channel: int, start_v: float, stop_v: float, step_v: float, delay_s=0.1):
        voltage = start_v
        step = abs(step_v) if stop_v > start_v else -abs(step_v)
        while (voltage <= stop_v if step > 0 else voltage >= stop_v):
            self.set_voltage(channel, voltage)
            time.sleep(delay_s)
            voltage += step
        self.set_voltage(channel, stop_v)

    # Application-level voltage sweep test
    def voltage_sweep_test(self, channel: int, start_v: float, stop_v: float, step_v: float, current_limit: float):
        print(f"Voltage sweep on channel {channel} from {start_v} V to {stop_v} V")
        self.set_current(channel, current_limit)
        self.output_on(channel)
        results = []
        voltage = start_v
        while voltage <= stop_v:
            self.set_voltage(channel, voltage)
            if not self.wait_for_voltage_stabilization(channel, voltage):
                print(f"Warning: Voltage did not stabilize at {voltage} V")
            meas_v = self.measure_voltage(channel)
            meas_i = self.measure_current(channel)
            print(f"Set V: {voltage:.3f} V, Meas V: {meas_v:.3f} V, Meas I: {meas_i:.3f} A")
            results.append({'Set_Voltage': voltage, 'Measured_Voltage': meas_v, 'Measured_Current': meas_i})
            voltage += step_v
        self.output_off(channel)
        return results

    # Close connection
    def close(self):
        self.supply.close()

# ---------------------------
# Example Usage
# ---------------------------

def example_usage():
    psu = E362X(port='GPIB0::7::INSTR')
    print("IDN:", psu.get_idn())

    channel = 1

    # Enable 4-wire remote sensing
    psu.enable_4wire_sense(channel)
    status = psu.query_4wire_sense_status(channel)
    print(f"4-wire sense status on channel {channel}: {status}")

    # Set voltage and current
    psu.set_voltage(channel, 5.0)
    psu.set_current(channel, 1.0)
    psu.output_on(channel)

    time.sleep(1)

    # Measure voltage and current
    v = psu.measure_voltage(channel)
    i = psu.measure_current(channel)
    print(f"Measured Voltage: {v:.3f} V, Current: {i:.3f} A")

    # Perform voltage sweep test
    results = psu.voltage_sweep_test(channel, start_v=3.0, stop_v=5.0, step_v=0.5, current_limit=1.0)
    for r in results:
        print(r)

    # Disable 4-wire remote sensing
    psu.disable_4wire_sense(channel)
    status = psu.query_4wire_sense_status(channel)
    print(f"4-wire sense status on channel {channel} after disable: {status}")

    psu.output_off(channel)
    psu.close()

if __name__ == "__main__":
    example_usage()
