import time
import pyvisa

class A34461:
    """
    Keysight 34461A Truevolt DMM SCPI Control Library.
    Includes full configuration, measurement, trigger, and application functions.
    """

    def __init__(self, resource_name):
        self.rm = pyvisa.ResourceManager()
        self.inst = self.rm.open_resource(resource_name)
        self.inst.timeout = 5000  # ms
        self.inst.read_termination = '\n'
        self.inst.write_termination = '\n'

        # Set default input impedance to AUTO (10 GΩ)
        self.set_input_impedance('AUTO')

    # --- Basic Instrument Control ---

    def identify(self):
        return self.inst.query("*IDN?").strip()

    def reset(self):
        self.inst.write("*RST")

    def clear_status(self):
        self.inst.write("*CLS")

    def self_test(self):
        return self.inst.query("*TST?").strip()

    def get_error(self):
        return self.inst.query("SYST:ERR?").strip()

    def get_options(self):
        return self.inst.query("*OPT?").strip()

    # --- Input Impedance ---

    def set_input_impedance(self, impedance='AUTO'):
        valid_values = ['AUTO', '10M', '50']
        if impedance not in valid_values:
            raise ValueError(f"Invalid impedance value. Valid options: {valid_values}")
        if impedance == 'AUTO':
            self.inst.write("INPUT:IMP AUTO")
        else:
            self.inst.write(f"INPUT:IMP {impedance}")

    def get_input_impedance(self):
        return self.inst.query("INPUT:IMP?").strip()

    # --- Configure Functions ---

    def configure_voltage_dc(self, range_val='AUTO', resolution=None):
        self.configure_function("VOLT:DC", range_val, resolution)

    def configure_voltage_ac(self, range_val='AUTO', resolution=None):
        self.configure_function("VOLT:AC", range_val, resolution)

    def configure_current_dc(self, range_val='AUTO', resolution=None):
        self.configure_function("CURR:DC", range_val, resolution)

    def configure_current_ac(self, range_val='AUTO', resolution=None):
        self.configure_function("CURR:AC", range_val, resolution)

    def configure_resistance(self, range_val='AUTO', resolution=None):
        self.configure_function("RES", range_val, resolution)

    def configure_frequency(self, range_val='AUTO', resolution=None):
        self.configure_function("FREQ", range_val, resolution)

    def configure_capacitance(self, range_val='AUTO', resolution=None):
        self.configure_function("CAP", range_val, resolution)

    def configure_temperature(self, sensor='T', range_val='AUTO', resolution=None):
        if sensor.upper() == 'RTD':
            func = "TEMP:RTD"
        else:
            func = "TEMP"
        self.configure_function(func, range_val, resolution)

    def configure_impedance(self, mode='Z', range_val='AUTO', resolution=None):
        self.configure_function(f"IMP:{mode}", range_val, resolution)

    def configure_function(self, func, range_val=None, resolution=None):
        cmd = f"CONF:{func}"
        if range_val is not None:
            cmd += f" {range_val}"
        if resolution is not None:
            cmd += f", {resolution}"
        self.inst.write(cmd)

    # --- Measurement Queries ---

    def measure(self):
        return float(self.inst.query("MEAS?"))

    def measure_voltage_dc(self):
        return float(self.inst.query("MEAS:VOLT:DC?"))

    def measure_voltage_ac(self):
        return float(self.inst.query("MEAS:VOLT:AC?"))

    def measure_current_dc(self):
        return float(self.inst.query("MEAS:CURR:DC?"))

    def measure_current_ac(self):
        return float(self.inst.query("MEAS:CURR:AC?"))

    def measure_resistance(self):
        return float(self.inst.query("MEAS:RES?"))

    def measure_frequency(self):
        return float(self.inst.query("MEAS:FREQ?"))

    def measure_capacitance(self):
        return float(self.inst.query("MEAS:CAP?"))

    def measure_temperature(self, sensor='T'):
        if sensor.upper() == 'RTD':
            return float(self.inst.query("MEAS:TEMP:RTD?"))
        else:
            return float(self.inst.query("MEAS:TEMP?"))

    def measure_impedance(self, mode='Z'):
        return float(self.inst.query(f"MEAS:IMP:{mode}?"))

    # --- Trigger and Sampling Control ---

    def set_trigger_source(self, source='IMM'):
        self.inst.write(f"TRIG:SOUR {source}")

    def get_trigger_source(self):
        return self.inst.query("TRIG:SOUR?").strip()

    def set_trigger_count(self, count):
        self.inst.write(f"TRIG:COUN {count}")

    def get_trigger_count(self):
        return int(self.inst.query("TRIG:COUN?"))

    def set_sample_count(self, count):
        self.inst.write(f"SAMP:COUN {count}")

    def get_sample_count(self):
        return int(self.inst.query("SAMP:COUN?"))

    def set_trigger_delay(self, delay_sec):
        self.inst.write(f"TRIG:DEL {delay_sec}")

    def get_trigger_delay(self):
        return float(self.inst.query("TRIG:DEL?"))

    def set_trigger_slope(self, slope='POS'):
        self.inst.write(f"OUTP:TRIG:SLOP {slope}")

    def get_trigger_slope(self):
        return self.inst.query("OUTP:TRIG:SLOP?").strip()

    def initiate_measurement(self):
        self.inst.write("INIT")

    def wait_for_operation_complete(self, timeout=10):
        self.inst.timeout = timeout * 1000
        return self.inst.query("*OPC?").strip() == '1'

    # --- Digital Trigger Detection and Status ---

    def enable_digital_trigger_detection(self, enable=True):
        state = 'ON' if enable else 'OFF'
        try:
            self.inst.write(f"TRIG:DEL:AUTO {state}")
        except Exception:
            pass

    def get_trigger_status(self):
        try:
            status = self.inst.query("TRIG:STAT?").strip()
            return status == '1'
        except Exception:
            cond = int(self.inst.query("STAT:OPER:COND?"))
            return bool(cond & 1)

    # --- Averaging and Filtering ---

    def set_averaging(self, count, enable=True):
        self.inst.write(f"SENS:AVER:COUN {count}")
        self.inst.write(f"SENS:AVER:STAT {'ON' if enable else 'OFF'}")

    def get_averaging(self):
        count = int(self.inst.query("SENS:AVER:COUN?"))
        status = self.inst.query("SENS:AVER:STAT?").strip()
        return count, status == 'ON'

    def set_filter(self, enable=True):
        self.inst.write(f"SENS:AVER:STAT {'ON' if enable else 'OFF'}")

    # --- Math Functions ---

    def set_math_function(self, func='DB', enable=True):
        self.inst.write(f"CALC:FUNC {func}")
        self.inst.write(f"CALC:STAT {'ON' if enable else 'OFF'}")

    def set_math_reference(self, value):
        self.inst.write(f"CALC:REF {value}")

    # --- Auto Range and Zero ---

    def set_auto_range(self, enable=True):
        state = 'ON' if enable else 'OFF'
        self.inst.write(f"SENS:VOLT:DC:RANG:AUTO {state}")

    def set_auto_zero(self, enable=True):
        state = 'ON' if enable else 'OFF'
        self.inst.write(f"SENS:ZERO:AUTO {state}")

    # --- Data Fetching and Logging ---

    def fetch_data(self):
        data_str = self.inst.query("FETCH?")
        return [float(x) for x in data_str.split(',')]

    def read_data(self, max_readings=1):
        resp = self.inst.query(f"READ? {max_readings}")
        return [float(x) for x in resp.split(',')]

    # --- Calibration and Security ---

    def calibrate_zero(self):
        self.inst.write("CAL:ZERO:STAT ON")

    def calibrate_full_scale(self):
        self.inst.write("CAL:FSCL:STAT ON")

    def secure_calibration(self, code="AT3446XA"):
        self.inst.write(f"CAL:SEC:STAT ON,{code}")

    def unsecure_calibration(self, code="AT3446XA"):
        self.inst.write(f"CAL:SEC:STAT OFF,{code}")

    # --- Application-Level Functions ---

    def initialize(self):
        self.reset()
        time.sleep(1)
        self.clear_status()
        self.set_input_impedance('AUTO')
        self.set_trigger_source('IMM')
        self.set_auto_range(True)
        self.set_auto_zero(True)
        self.set_averaging(1, enable=False)

    def measure_average(self, func='VOLT:DC', samples=10, delay=0.1):
        self.configure_function(func)
        readings = []
        for _ in range(samples):
            self.initiate_measurement()
            time.sleep(delay)
            val = self.measure()
            readings.append(val)
        return sum(readings) / len(readings)

    def run_continuous_measurement(self, func='VOLT:DC', sample_count=10, delay=0.5):
        self.configure_function(func)
        self.set_sample_count(sample_count)
        self.set_trigger_source('IMM')
        self.initiate_measurement()
        results = []
        for _ in range(sample_count):
            time.sleep(delay)
            val = self.measure()
            results.append(val)
        return results

    def simulate_input_signal(self):
        print("Simulation mode not supported on 34461A.")

    # --- Close connection ---

    def close(self):
        self.inst.close()
        self.rm.close()
