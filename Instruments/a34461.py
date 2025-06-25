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
        self.inst.timeout = 15000
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
        """
        Set the input impedance of the instrument.
    
        Args:
            impedance (str): Input impedance setting. Valid options are:
                             'AUTO' - automatic impedance,
                             '10M'  - 10 Megaohms,
                             '50'   - 50 Ohms.
    
        Raises:
            ValueError: If the impedance value is invalid.
        """
        valid_values = ['AUTO', '10M', '50']
        impedance = impedance.upper()  # Normalize input to uppercase for case-insensitive matching
        if impedance not in valid_values:
            raise ValueError(f"Invalid impedance value '{impedance}'. Valid options: {valid_values}")
    
        # Map '10M' to '10M' and '50' to '50' as expected by the instrument
        # 'AUTO' is sent as is
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

    def run_continuous_measurement(self, func='VOLT:DC', sample_count=1, delay=0.5):
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

# ---------------------------
    # Voltage AC Bandwidth Filter
    # ---------------------------
    def set_voltage_ac_bandwidth(self, value):
            """
            Set the AC voltage bandwidth filter based on the lowest expected input frequency.

            The instrument selects one of three filters to optimize measurement accuracy and settling time:

            +----------------------------+-------------------------+-------------------------+
            | Input Frequency Range (Hz) | Filter Bandwidth (Hz)   | Typical Settling Delay  |
            +----------------------------+-------------------------+-------------------------+
            | 3 Hz - 20 Hz               | 3 (Slow)                | 2.5000 seconds/measurement|
            | > 20 Hz - 200 Hz           | 20 (Medium)             | 0.6250 seconds/measurement|
            | > 200 Hz - 300 kHz         | 200 (Fast)              | 0.0250 seconds/measurement|
            +----------------------------+-------------------------+-------------------------+

            Parameters:
                value (float|int|str): Lowest expected frequency in Hz or keyword ('MIN', 'MAX', 'DEF').

            Behavior:
                - Numeric frequency selects corresponding filter bandwidth as per the table above.
                - Keywords 'MIN', 'MAX', 'DEF' are passed directly to the instrument.

            Raises:
                ValueError: If input is invalid.

            Example:
                set_voltage_ac_bandwidth(15)  # selects 3 Hz filter (slow)
                set_voltage_ac_bandwidth(100) # selects 20 Hz filter (medium)
                set_voltage_ac_bandwidth(300) # selects 200 Hz filter (fast)
                set_voltage_ac_bandwidth('DEF') # uses instrument default filter
            """
            if isinstance(value, str):
                value_upper = value.strip().upper()
                if value_upper in {"MIN", "MAX", "DEF"}:
                    self.inst.write(f"SENSe:VOLTage:AC:BANDwidth {value_upper}")
                    return
                try:
                    value = float(value)
                except ValueError:
                    raise ValueError("Invalid input: must be frequency (Hz) or one of 'MIN', 'MAX', 'DEF'.")

            if value <= 20:
                filter_value = 3
            elif value <= 200:
                filter_value = 20
            else:
                filter_value = 200

            self.inst.write(f"SENSe:VOLTage:AC:BANDwidth {filter_value}")


    def get_voltage_ac(self):
            """
            Query and return the measured AC voltage.
    
            Returns:
                str: Measured AC voltage reading from the instrument.
            """
            return self.inst.query("MEASure:VOLTage:AC?").strip()

    # ---------------------------
    # Voltage AC/DC Null State
    # ---------------------------
    def set_voltage_null_state(self, ac_dc, state):
        """
        Enable or disable the null function for AC or DC voltage measurements.

        Parameters:
            ac_dc (str): 'AC' or 'DC' to specify the measurement type.
            state (str|int): 'ON', 'OFF', 1, or 0 to enable or disable the null function.

        Raises:
            ValueError: If ac_dc or state parameters are invalid.

        Usage example:
            set_voltage_null_state('AC', 'ON')
            set_voltage_null_state('DC', 0)
        """
        ac_dc = ac_dc.upper()
        if ac_dc not in ['AC', 'DC']:
            raise ValueError("ac_dc must be 'AC' or 'DC'")

        # Normalize state input to instrument-acceptable string
        if isinstance(state, str):
            state_upper = state.upper()
            if state_upper in ['ON', '1']:
                state_str = 'ON'
            elif state_upper in ['OFF', '0']:
                state_str = 'OFF'
            else:
                raise ValueError("state must be 'ON', 'OFF', 1, or 0")
        elif isinstance(state, int):
            if state == 1:
                state_str = 'ON'
            elif state == 0:
                state_str = 'OFF'
            else:
                raise ValueError("state must be 1 or 0")
        else:
            raise ValueError("state must be a string ('ON'/'OFF') or integer (1/0)")

        self.inst.write(f"SENSe:VOLTage:{ac_dc}:NULL:STATe {state_str}")

    def get_voltage_null_state(self, ac_dc):
        """
        Query the null state for AC or DC voltage measurements.

        Parameters:
            ac_dc (str): 'AC' or 'DC' to specify the measurement type.

        Returns:
            str: 'ON' or 'OFF' indicating the null function state.

        Raises:
            ValueError: If ac_dc parameter is invalid.

        Usage example:
            state = get_voltage_null_state('AC')
            print(f"AC Null State: {state}")
        """
        ac_dc = ac_dc.upper()
        if ac_dc not in ['AC', 'DC']:
            raise ValueError("ac_dc must be 'AC' or 'DC'")

        response = self.inst.query(f"SENSe:VOLTage:{ac_dc}:NULL:STATe?").strip()
        # Normalize response to 'ON' or 'OFF'
        if response in ['1', 'ON']:
            return 'ON'
        elif response in ['0', 'OFF']:
            return 'OFF'
        else:
            # Unexpected response, return as-is or raise error
            return response

    # ---------------------------
    # Voltage AC/DC Null Value Set
    # ---------------------------
    def set_voltage_null_value(self, ac_dc, value=None):
        """
        Set the null value for AC or DC voltage measurements.

        Parameters:
            ac_dc (str): 'AC' or 'DC' to specify the measurement type.
            value (float|int|str|None): Null value to subtract from measurements.
                - Numeric values must be between -1200 and +1200 (Volts).
                - Special keywords: 'MIN', 'MAX', 'DEF'.
                - None means no command sent (no change).

        Raises:
            ValueError: If ac_dc or value is invalid.

        Usage examples:
            set_voltage_null_value('AC', 0.1)       # Subtract 100 mV
            set_voltage_null_value('DC', 'MIN')    # Use minimum null value
            set_voltage_null_value('AC', None)     # Do not change null value
        """
        ac_dc = ac_dc.upper()
        if ac_dc not in ['AC', 'DC']:
            raise ValueError("ac_dc must be 'AC' or 'DC'")

        if value is None:
            # Do not send any command if value is None
            return

        if isinstance(value, (int, float)):
            if not (-1200 <= value <= 1200):
                raise ValueError("Null value must be between -1200 and +1200 Volts")
            value_str = f"{value}"
        elif isinstance(value, str):
            value_upper = value.upper()
            if value_upper in {'MIN', 'MAX', 'DEF'}:
                value_str = value_upper
            else:
                # Try to parse numeric string
                try:
                    numeric_value = float(value)
                    if not (-1200 <= numeric_value <= 1200):
                        raise ValueError("Null value must be between -1200 and +1200 Volts")
                    value_str = f"{numeric_value}"
                except ValueError:
                    raise ValueError("Value must be a number or one of 'MIN', 'MAX', 'DEF'")
        else:
            raise ValueError("Value must be a number, string keyword, or None")

        self.inst.write(f"SENSe:VOLTage:{ac_dc}:NULL:VALue {value_str}")

    def get_voltage_null_value(self, ac_dc, query_type=None):
        """
        Query the null value for AC or DC voltage measurements.

        Parameters:
            ac_dc (str): 'AC' or 'DC' to specify the measurement type.
            query_type (str|None): Optional query parameter:
                - 'MIN', 'MAX', or 'DEF' to query special values.
                - None to query the current null value.

        Returns:
            str: The instrument's response (usually a numeric string or keyword).

        Raises:
            ValueError: If ac_dc or query_type is invalid.

        Usage examples:
            val = get_voltage_null_value('AC')          # Query current null value
            val_min = get_voltage_null_value('DC', 'MIN')  # Query minimum null value
        """
        ac_dc = ac_dc.upper()
        if ac_dc not in ['AC', 'DC']:
            raise ValueError("ac_dc must be 'AC' or 'DC'")

        if query_type is not None:
            query_type_upper = query_type.upper()
            if query_type_upper not in {'MIN', 'MAX', 'DEF'}:
                raise ValueError("query_type must be one of 'MIN', 'MAX', 'DEF' or None")
            response = self.inst.query(f"SENSe:VOLTage:{ac_dc}:NULL:VALue? {query_type_upper}")
        else:
            response = self.inst.query(f"SENSe:VOLTage:{ac_dc}:NULL:VALue?")

        return response.strip()
    # ---------------------------
    # Voltage AC/DC Null Value Auto
    # ---------------------------
    def set_voltage_null_value_auto(self, ac_dc, state):
        """Enable or disable auto null value for AC or DC voltage"""
        ac_dc = ac_dc.upper()
        if ac_dc not in ['AC', 'DC']:
            raise ValueError("ac_dc must be 'AC' or 'DC'")
        state = state.upper()
        if state not in ['ON', 'OFF']:
            raise ValueError("state must be 'ON' or 'OFF'")
        self.inst.write(f"SENSe:VOLTage:{ac_dc}:NULL:VALue:AUTO {state}")

    def get_voltage_null_value_auto(self, ac_dc):
        """Query auto null value state for AC or DC voltage"""
        ac_dc = ac_dc.upper()
        if ac_dc not in ['AC', 'DC']:
            raise ValueError("ac_dc must be 'AC' or 'DC'")
        return self.inst.query(f"SENSe:VOLTage:{ac_dc}:NULL:VALue:AUTO?").strip()

    # ---------------------------
    # Voltage AC/DC Range
    # ---------------------------
    def set_voltage_range_auto(self, ac_dc, state):
        """
        Set auto range state for AC or DC voltage measurements.

        Parameters:
            ac_dc (str): 'AC' or 'DC'
            state (str): 'OFF', 'ON', or 'ONCE'

        Raises:
            ValueError: If parameters are invalid.

        Notes:
            - Setting a fixed range disables autoranging.
        """
        ac_dc = ac_dc.upper()
        if ac_dc not in ['AC', 'DC']:
            raise ValueError("ac_dc must be 'AC' or 'DC'")

        state = state.upper()
        if state not in ['OFF', 'ON', 'ONCE']:
            raise ValueError("state must be 'OFF', 'ON', or 'ONCE'")

        self.inst.write(f"SENSe:VOLTage:{ac_dc}:RANGe:AUTO {state}")

    def get_voltage_range_auto(self, ac_dc):
        """
        Query auto range state for AC or DC voltage measurements.

        Parameters:
            ac_dc (str): 'AC' or 'DC'

        Returns:
            str: 'OFF', 'ON', or 'ONCE'

        Raises:
            ValueError: If ac_dc is invalid.
        """
        ac_dc = ac_dc.upper()
        if ac_dc not in ['AC', 'DC']:
            raise ValueError("ac_dc must be 'AC' or 'DC'")

        return self.inst.query(f"SENSe:VOLTage:{ac_dc}:RANGe:AUTO?").strip()

    def set_voltage_range(self, ac_dc, range_value):
        """
        Set fixed measurement range for AC or DC voltage measurements.

        Parameters:
            ac_dc (str): 'AC' or 'DC'
            range_value (str|float|int): Range to set. Acceptable values:
                - Numeric or string values: 0.1, 1, 10, 100, 1000 (Volts)
                - String with units: '100 mV', '1 V', '10 V', '100 V', '1000 V'
                - Keywords: 'MIN', 'MAX', 'DEF'

        Raises:
            ValueError: If parameters are invalid.

        Notes:
            - Selecting a fixed range disables autoranging.
            - The max allowed range is 1000 V.
            - The default ranges are 10 V for AC and 1000 V for DC.
        """
        ac_dc = ac_dc.upper()
        if ac_dc not in ['AC', 'DC']:
            raise ValueError("ac_dc must be 'AC' or 'DC'")

        # Normalize range_value to string
        valid_ranges = {
            '100 mV': 0.1,
            '0.1': 0.1,
            '1 V': 1,
            '1': 1,
            '10 V': 10,
            '10': 10,
            '100 V': 100,
            '100': 100,
            '1000 V': 1000,
            '1000': 1000,
            'MIN': 'MIN',
            'MAX': 'MAX',
            'DEF': 'DEF'
        }

        # Convert numeric inputs to string with units if needed
        if isinstance(range_value, (int, float)):
            if range_value not in [0.1, 1, 10, 100, 1000]:
                raise ValueError("Range must be one of 0.1, 1, 10, 100, 1000 Volts")
            # Convert to string without units, instrument accepts numeric values
            range_str = str(range_value)
        elif isinstance(range_value, str):
            range_value_clean = range_value.strip().upper().replace(' ', '')
            # Try to match keys ignoring spaces and case
            matched_key = None
            for key in valid_ranges.keys():
                if key.replace(' ', '').upper() == range_value_clean:
                    matched_key = key
                    break
            if matched_key is None:
                raise ValueError(f"Invalid range value: {range_value}")
            range_str = matched_key if matched_key in ['MIN', 'MAX', 'DEF'] else str(valid_ranges[matched_key])
        else:
            raise ValueError("range_value must be a string or numeric")

        self.inst.write(f"SENSe:VOLTage:{ac_dc}:RANGe {range_str}")

    def get_voltage_range(self, ac_dc, query_type=None):
        """
        Query the fixed measurement range for AC or DC voltage measurements.

        Parameters:
            ac_dc (str): 'AC' or 'DC'
            query_type (str|None): Optional query parameter:
                - 'MIN', 'MAX', 'DEF' to query special ranges
                - None to query current range

        Returns:
            str: Current range or special range value.

        Raises:
            ValueError: If parameters are invalid.
        """
        ac_dc = ac_dc.upper()
        if ac_dc not in ['AC', 'DC']:
            raise ValueError("ac_dc must be 'AC' or 'DC'")

        if query_type is not None:
            query_type = query_type.upper()
            if query_type not in ['MIN', 'MAX', 'DEF']:
                raise ValueError("query_type must be one of 'MIN', 'MAX', 'DEF' or None")
            response = self.inst.query(f"SENSe:VOLTage:{ac_dc}:RANGe? {query_type}")
        else:
            response = self.inst.query(f"SENSe:VOLTage:{ac_dc}:RANGe?")

        return response.strip()

    # ---------------------------
    # Voltage AC Secondary Function
    # ---------------------------
    def set_voltage_ac_secondary(self, mode):
        """Set AC voltage secondary function (OFF, CALCulate:DATA, FREQuency, VOLTage[:DC])"""
        valid_modes = ['OFF', 'CALCulate:DATA', 'FREQuency', 'VOLTage', 'VOLTage:DC']
        if mode.upper() not in [m.upper() for m in valid_modes]:
            raise ValueError(f"Invalid mode. Valid options: {valid_modes}")
        self.inst.write(f'SENSe:VOLTage:AC:SECondary {mode}')

    def get_voltage_ac_secondary(self):
        """Query AC voltage secondary function"""
        return self.inst.query("SENSe:VOLTage:AC:SECondary?").strip()

    # ---------------------------
    # Voltage DC Aperture
    # ---------------------------
    def set_voltage_dc_aperture(self, value):
        """
        Set DC voltage aperture time (integration time) in seconds or special keywords.

        Parameters:
            value (float|int|str): Aperture time in seconds (e.g., 0.1 for 100 ms),
                                  or one of the keywords: 'MIN', 'MAX', 'DEF'.

        Raises:
            ValueError: If the value is invalid.

        Notes:
            - Setting aperture time enables aperture mode automatically.
            - Typical valid range is 20 μs (0.00002 s) to 1 s.
            - Resolution: 2 μs.
            - Setting aperture overrides NPLC setting.
        """
        valid_keywords = {'MIN', 'MAX', 'DEF'}

        if isinstance(value, str):
            val_upper = value.strip().upper()
            if val_upper in valid_keywords:
                cmd_value = val_upper
            else:
                # Try to convert to float
                try:
                    val_float = float(value)
                    if not (0.00002 <= val_float <= 1):
                        raise ValueError("Aperture time must be between 20 μs and 1 s")
                    cmd_value = f"{val_float}"
                except ValueError:
                    raise ValueError(f"Invalid aperture time value: {value}")
        elif isinstance(value, (float, int)):
            if not (0.00002 <= value <= 1):
                raise ValueError("Aperture time must be between 20 μs and 1 s")
            cmd_value = f"{value}"
        else:
            raise ValueError("Aperture time must be a float, int, or one of 'MIN', 'MAX', 'DEF'")

        # Setting aperture time enables aperture mode automatically per documentation
        self.inst.write(f"SENSe:VOLTage:DC:APERture {cmd_value}")
        self.set_voltage_dc_aperture_enabled('ON')

    def get_voltage_dc_aperture(self, query_type=None):
        """
        Query DC voltage aperture time.

        Parameters:
            query_type (str|None): Optional. One of 'MIN', 'MAX', 'DEF' to query special aperture values.

        Returns:
            str: Aperture time in seconds or keyword.

        Raises:
            ValueError: If query_type is invalid.
        """
        if query_type is not None:
            query_type_upper = query_type.strip().upper()
            if query_type_upper not in {'MIN', 'MAX', 'DEF'}:
                raise ValueError("query_type must be one of 'MIN', 'MAX', 'DEF' or None")
            response = self.inst.query(f"SENSe:VOLTage:DC:APERture? {query_type_upper}")
        else:
            response = self.inst.query("SENSe:VOLTage:DC:APERture?")
        return response.strip()

    def set_voltage_dc_aperture_enabled(self, state):
        """
        Enable or disable DC voltage aperture mode.

        Parameters:
            state (str|int): 'ON', 'OFF', 1, or 0.

        Raises:
            ValueError: If state is invalid.

        Notes:
            - Default is OFF.
            - Enabling aperture mode means integration time is controlled by aperture time, not NPLC.
        """
        if isinstance(state, str):
            state_upper = state.strip().upper()
            if state_upper in ['ON', '1']:
                state_cmd = 'ON'
            elif state_upper in ['OFF', '0']:
                state_cmd = 'OFF'
            else:
                raise ValueError("state must be 'ON', 'OFF', 1, or 0")
        elif isinstance(state, int):
            if state == 1:
                state_cmd = 'ON'
            elif state == 0:
                state_cmd = 'OFF'
            else:
                raise ValueError("state must be 1 or 0")
        else:
            raise ValueError("state must be a string ('ON'/'OFF') or integer (1/0)")

        self.inst.write(f"SENSe:VOLTage:DC:APERture:ENABled {state_cmd}")

    def get_voltage_dc_aperture_enabled(self):
        """
        Query DC voltage aperture enable state.

        Returns:
            str: 'ON' or 'OFF'
        """
        response = self.inst.query("SENSe:VOLTage:DC:APERture:ENABled?")
        val = response.strip()
        if val in ['1', 'ON']:
            return 'ON'
        elif val in ['0', 'OFF']:
            return 'OFF'
        else:
            return val  # Unexpected response, return as-is


    # ---------------------------
    # Voltage DC Impedance Auto
    # ---------------------------
    def set_voltage_dc_impedance_auto(self, state):
        """Enable or disable DC voltage input impedance auto (ON or OFF)"""
        state = state.upper()
        if state not in ['ON', 'OFF']:
            raise ValueError("state must be 'ON' or 'OFF'")
        self.inst.write(f"SENSe:VOLTage:DC:IMPedance:AUTO {state}")

    def get_voltage_dc_impedance_auto(self):
        """Query DC voltage input impedance auto state"""
        return self.inst.query("SENSe:VOLTage:DC:IMPedance:AUTO?").strip()

    # ---------------------------
    # Voltage DC NPLC (Number of Power Line Cycles)
    # ---------------------------
    def set_voltage_dc_nplc(self, value):
        """Set DC voltage NPLC (Number of Power Line Cycles)"""
        self.inst.write(f"SENSe:VOLTage:DC:NPLC {value}")

    def get_voltage_dc_nplc(self):
        """Query DC voltage NPLC"""
        return self.inst.query("SENSe:VOLTage:DC:NPLC?").strip()

    # ---------------------------
    # Voltage DC Ratio Secondary
    # ---------------------------
    def set_voltage_dc_ratio_secondary(self, mode):
        """Set DC voltage ratio secondary function (OFF, CALCulate:DATA, SENSe:DATA)"""
        valid_modes = ['OFF', 'CALCulate:DATA', 'SENSe:DATA']
        if mode.upper() not in [m.upper() for m in valid_modes]:
            raise ValueError(f"Invalid mode. Valid options: {valid_modes}")
        self.inst.write(f"SENSe:VOLTage:DC:RATio:SECondary {mode}")

    def get_voltage_dc_ratio_secondary(self):
        """Query DC voltage ratio secondary function"""
        return self.inst.query("SENSe:VOLTage:DC:RATio:SECondary?").strip()

    # ---------------------------
    # Voltage DC Resolution
    # ---------------------------
    def set_voltage_dc_resolution(self, value):
        """Set DC voltage resolution (digits)"""
        self.inst.write(f"SENSe:VOLTage:DC:RESolution {value}")

    def get_voltage_dc_resolution(self):
        """Query DC voltage resolution"""
        return self.inst.query("SENSe:VOLTage:DC:RESolution?").strip()

    # ---------------------------
    # Voltage DC Secondary Function
    # ---------------------------
    def set_voltage_dc_secondary(self, mode):
        """Set DC voltage secondary function (OFF, CALCulate:DATA, VOLTage:AC, PTPeak)"""
        valid_modes = ['OFF', 'CALCulate:DATA', 'VOLTage:AC', 'PTPeak']
        if mode.upper() not in [m.upper() for m in valid_modes]:
            raise ValueError(f"Invalid mode. Valid options: {valid_modes}")
        self.inst.write(f"SENSe:VOLTage:DC:SECondary {mode}")

    def get_voltage_dc_secondary(self):
        """Query DC voltage secondary function"""
        return self.inst.query("SENSe:VOLTage:DC:SECondary?").strip()

    # ---------------------------
    # Voltage DC Zero Auto
    # ---------------------------
    def set_voltage_dc_zero_auto(self, state):
        """Set DC voltage zero auto mode (OFF, ON, ONCE)"""
        valid_states = ['OFF', 'ON', 'ONCE']
        if state.upper() not in valid_states:
            raise ValueError(f"Invalid state. Valid options: {valid_states}")
        self.inst.write(f"SENSe:VOLTage:DC:ZERO:AUTO {state}")

    def get_voltage_dc_zero_auto(self):
        """Query DC voltage zero auto mode"""
        return self.inst.query("SENSe:VOLTage:DC:ZERO:AUTO?").strip()
    
    def configure_voltmeter(self, voltage_range=None, resolution=None,
                             aperture_time=None, autozero=None, impedance=None):
        """
        Configure DC voltage measurement with specified range, resolution, aperture time,
        autozero, and input impedance.

        Args:
            voltage_range (float or str): Measurement range in volts (e.g., 1, 10, 100) or 'AUTO' for auto range.
                                          If None, defaults to 'AUTO'.
            resolution (float): Resolution in volts (e.g., 3e-6). If None, defaults to minimum resolution for range.
            aperture_time (float or str): Aperture time in seconds (e.g., 0.1) or 'MIN', 'MAX', 'DEF'.
                                         If None, aperture time is not set.
            autozero (str or int): 'ON', 'OFF', 1, or 0 to enable/disable autozero.
                                  If None, autozero is not changed.
            impedance (str): Input impedance setting, e.g., 'AUTO', '10M', '1G'.
                             If None, impedance is not changed.

        Raises:
            ValueError: If any parameter is invalid or incompatible.

        Notes:
            - Setting aperture_time enables aperture mode automatically.
            - If voltage_range is 'AUTO', autorange is enabled.
            - If voltage_range is numeric, autorange is disabled and fixed range is set.
            - Autozero and impedance settings are applied if provided.
        """
        # --- Validate and set voltage range and resolution ---

        valid_ranges = [1e-3, 10e-3, 100e-3, 1, 10, 100, 1e3, 10e3, 100e3, 1e6, 10e6, 100e6]

        if voltage_range is None:
            voltage_range = 'AUTO'

        if voltage_range != 'AUTO':
            # Validate numeric range approximately
            if not any(abs(voltage_range - r) / r < 0.1 for r in valid_ranges):
                raise ValueError(f"Invalid voltage range: {voltage_range}. Valid ranges: {valid_ranges} or 'AUTO'")

        default_resolution_map = {
            1e-3: 3e-9,
            10e-3: 3e-8,
            100e-3: 3e-7,
            1: 3e-6,
            10: 3e-5,
            100: 3e-4,
            1e3: 3e-3,
            10e3: 3e-2,
            100e3: 3e-1,
            1e6: 3,
            10e6: 30,
            100e6: 300
        }

        if resolution is None:
            if voltage_range == 'AUTO':
                resolution = 3e-6  # Typical default for auto range
            else:
                closest_range = min(default_resolution_map.keys(), key=lambda x: abs(x - voltage_range))
                resolution = default_resolution_map[closest_range]

        # Compose configure voltage command
        if voltage_range == 'AUTO':
            # Enable autorange
            self.inst.write("SENSe:VOLTage:DC:RANGe:AUTO ON")
            # Use DEF range with specified resolution
            cmd = f"CONFigure:VOLTage:DC DEF,{resolution}"
        else:
            # Disable autorange and set fixed range
            self.inst.write("SENSe:VOLTage:DC:RANGe:AUTO OFF")
            cmd = f"CONFigure:VOLTage:DC {voltage_range},{resolution}"

        self.inst.write(cmd)

        # --- Set aperture time if provided ---
        if aperture_time is not None:
            valid_aperture_keywords = {'MIN', 'MAX', 'DEF'}
            if isinstance(aperture_time, str):
                ap_upper = aperture_time.strip().upper()
                if ap_upper not in valid_aperture_keywords:
                    try:
                        ap_val = float(aperture_time)
                        if not (0.00002 <= ap_val <= 1):
                            raise ValueError("Aperture time must be between 20 μs and 1 s")
                    except ValueError:
                        raise ValueError("Invalid aperture_time string value")
                # Send aperture command (this enables aperture mode automatically)
                self.inst.write(f"SENSe:VOLTage:DC:APERture {aperture_time}")
                self.inst.write("SENSe:VOLTage:DC:APERture:ENABled ON")
            elif isinstance(aperture_time, (float, int)):
                if not (0.00002 <= aperture_time <= 1):
                    raise ValueError("Aperture time must be between 20 μs and 1 s")
                self.inst.write(f"SENSe:VOLTage:DC:APERture {aperture_time}")
                self.inst.write("SENSe:VOLTage:DC:APERture:ENABled ON")
            else:
                raise ValueError("aperture_time must be float, int, or one of 'MIN', 'MAX', 'DEF'")

        # --- Set autozero if provided ---
        if autozero is not None:
            if isinstance(autozero, str):
                az_upper = autozero.strip().upper()
                if az_upper in ['ON', '1']:
                    az_cmd = 'ON'
                elif az_upper in ['OFF', '0']:
                    az_cmd = 'OFF'
                else:
                    raise ValueError("autozero must be 'ON', 'OFF', 1, or 0")
            elif isinstance(autozero, int):
                if autozero == 1:
                    az_cmd = 'ON'
                elif autozero == 0:
                    az_cmd = 'OFF'
                else:
                    raise ValueError("autozero must be 'ON', 'OFF', 1, or 0")
            else:
                raise ValueError("autozero must be string or int")

            self.inst.write(f"SENSe:VOLTage:DC:AUTozero {az_cmd}")

        # --- Set input impedance if provided ---
        if impedance is not None:
            # Typical impedance settings: 'AUTO', '10M', '1G'
            valid_impedances = {'AUTO', '10M', '1G'}
            imp_upper = str(impedance).strip().upper()
            if imp_upper not in valid_impedances:
                raise ValueError(f"Invalid impedance setting: {impedance}. Valid: {valid_impedances}")
            self.inst.write(f"SENSe:VOLTage:DC:IMPedance {imp_upper}")

    # ---------------------------
    # Trigger functuions 
    # ---------------------------
    def set_trigger_count(self, count):
        """
        Set the number of trigger events.

        Args:
            count (int): Number of triggers (positive integer).

        Raises:
            ValueError: If count is not a positive integer.
        """
        if not isinstance(count, int) or count <= 0:
            raise ValueError("Trigger count must be a positive integer")
        self.inst.write(f"TRIGger:COUNt {count}")

    def get_trigger_count(self):
        """Query the number of trigger events."""
        return int(self.inst.query("TRIGger:COUNt?").strip())

    def set_trigger_delay(self, delay_seconds):
        """
        Set fixed trigger delay time.

        Args:
            delay_seconds (float): Delay time in seconds (>= 0).

        Raises:
            ValueError: If delay_seconds is negative.
        """
        if delay_seconds < 0:
            raise ValueError("Trigger delay must be non-negative")
        self.inst.write(f"TRIGger:DELay {delay_seconds}")

    def get_trigger_delay(self):
        """Query the fixed trigger delay time in seconds."""
        return float(self.inst.query("TRIGger:DELay?").strip())

    def set_trigger_delay_auto(self, enabled):
        """
        Enable or disable automatic trigger delay.

        Args:
            enabled (bool or str or int): True/'ON'/1 to enable, False/'OFF'/0 to disable.

        Raises:
            ValueError: If enabled is not recognized.
        """
        state = self._bool_to_on_off(enabled)
        self.inst.write(f"TRIGger:DELay:AUTO {state}")

    def get_trigger_delay_auto(self):
        """Query if automatic trigger delay is enabled. Returns 'ON' or 'OFF'."""
        return self.inst.query("TRIGger:DELay:AUTO?").strip()

    def set_trigger_level(self, level):
        """
        Set the trigger level.

        Args:
            level (float): Trigger level voltage (units depend on measurement).

        Raises:
            ValueError: If level is not a float or int.
        """
        if not isinstance(level, (float, int)):
            raise ValueError("Trigger level must be a numeric value")
        self.inst.write(f"TRIGger:LEVel {level}")

    def get_trigger_level(self):
        """Query the trigger level."""
        return float(self.inst.query("TRIGger:LEVel?").strip())

    def set_trigger_slope(self, slope):
        """
        Set trigger slope.

        Args:
            slope (str): 'POSitive' or 'NEGative'

        Raises:
            ValueError: If slope is invalid.
        """
        slope_upper = slope.strip().upper()
        if slope_upper not in ['POSITIVE', 'NEGATIVE']:
            raise ValueError("Slope must be 'POSitive' or 'NEGative'")
        self.inst.write(f"TRIGger:SLOPe {slope_upper}")

    def get_trigger_slope(self):
        """Query the trigger slope."""
        return self.inst.query("TRIGger:SLOPe?").strip()

    def set_trigger_source(self, source):
        """
        Set the trigger source.

        Args:
            source (str): Valid trigger source, e.g., 'IMM', 'EXT', 'BUS', 'TIM', etc.

        Raises:
            ValueError: If source is invalid.
        """
        valid_sources = ['IMM', 'EXT', 'BUS', 'TIM', 'MAN', 'SWEEP']  # Extend as per manual
        source_upper = source.strip().upper()
        if source_upper not in valid_sources:
            raise ValueError(f"Invalid trigger source. Valid options: {valid_sources}")
        self.inst.write(f"TRIGger:SOURce {source_upper}")

    def get_trigger_source(self):
        """Query the trigger source."""
        return self.inst.query("TRIGger:SOURce?").strip()

    def _bool_to_on_off(self, value):
        """
        Helper to convert bool/int/str to 'ON' or 'OFF' string.
        """
        if isinstance(value, bool):
            return 'ON' if value else 'OFF'
        if isinstance(value, int):
            if value == 1:
                return 'ON'
            elif value == 0:
                return 'OFF'
        if isinstance(value, str):
            val_upper = value.strip().upper()
            if val_upper in ['ON', '1', 'TRUE']:
                return 'ON'
            elif val_upper in ['OFF', '0', 'FALSE']:
                return 'OFF'
        raise ValueError("Value must be boolean, 1/0, or 'ON'/'OFF' string")
        # ---------------------------
    # AC Current Bandwidth Filter
    # ---------------------------
    def set_current_ac_bandwidth(self, value):
        """
        Set AC current bandwidth filter.

        Args:
            value (str|int): Filter bandwidth in Hz (e.g., 3, 20, 200) or keyword 'MIN', 'MAX', 'DEF'.

        Raises:
            ValueError: If value is invalid.
        """
        valid_keywords = {'MIN', 'MAX', 'DEF'}
        if isinstance(value, str):
            val_upper = value.strip().upper()
            if val_upper not in valid_keywords:
                try:
                    int_val = int(value)
                    if int_val not in {3, 20, 200}:
                        raise ValueError
                    value = int_val
                except Exception:
                    raise ValueError("Invalid AC bandwidth filter. Use 3, 20, 200 or 'MIN', 'MAX', 'DEF'.")
            else:
                value = val_upper
        elif isinstance(value, int):
            if value not in {3, 20, 200}:
                raise ValueError("Invalid AC bandwidth filter. Use 3, 20, or 200 Hz.")
        else:
            raise ValueError("Value must be int or one of 'MIN', 'MAX', 'DEF'.")

        self.inst.write(f"SENSe:CURRent:AC:BANDwidth {value}")

    def get_current_ac_bandwidth(self, query_type=None):
        """
        Query AC current bandwidth filter.

        Args:
            query_type (str|None): Optional 'MIN', 'MAX', or 'DEF'.

        Returns:
            str: Current bandwidth setting.
        """
        if query_type:
            query_type = query_type.strip().upper()
            if query_type not in {'MIN', 'MAX', 'DEF'}:
                raise ValueError("query_type must be 'MIN', 'MAX', or 'DEF'")
            response = self.inst.query(f"SENSe:CURRent:AC:BANDwidth? {query_type}")
        else:
            response = self.inst.query("SENSe:CURRent:AC:BANDwidth?")
        return response.strip()

    # ---------------------------
    # Current Null State
    # ---------------------------
    def set_current_null_state(self, ac_dc, state):
        """
        Enable or disable null state for AC or DC current.

        Args:
            ac_dc (str): 'AC' or 'DC'.
            state (str): 'ON' or 'OFF'.

        Raises:
            ValueError: If parameters invalid.
        """
        ac_dc = ac_dc.upper()
        state = state.upper()
        if ac_dc not in {'AC', 'DC'}:
            raise ValueError("ac_dc must be 'AC' or 'DC'")
        if state not in {'ON', 'OFF'}:
            raise ValueError("state must be 'ON' or 'OFF'")
        self.inst.write(f"SENSe:CURRent:{ac_dc}:NULL:STATe {state}")

    def get_current_null_state(self, ac_dc):
        """
        Query null state for AC or DC current.

        Args:
            ac_dc (str): 'AC' or 'DC'.

        Returns:
            str: 'ON' or 'OFF'.
        """
        ac_dc = ac_dc.upper()
        if ac_dc not in {'AC', 'DC'}:
            raise ValueError("ac_dc must be 'AC' or 'DC'")
        return self.inst.query(f"SENSe:CURRent:{ac_dc}:NULL:STATe?").strip()

    # ---------------------------
    # Current Null Value
    # ---------------------------
    def set_current_null_value(self, ac_dc, value):
        """
        Set null value for AC or DC current.

        Args:
            ac_dc (str): 'AC' or 'DC'.
            value (float|str): Numeric value or 'MIN', 'MAX', 'DEF'.

        Raises:
            ValueError: If invalid inputs.
        """
        ac_dc = ac_dc.upper()
        if ac_dc not in {'AC', 'DC'}:
            raise ValueError("ac_dc must be 'AC' or 'DC'")

        if isinstance(value, str):
            val_upper = value.strip().upper()
            if val_upper not in {'MIN', 'MAX', 'DEF'}:
                try:
                    float(value)
                except ValueError:
                    raise ValueError("value must be float or one of 'MIN', 'MAX', 'DEF'")
            value = val_upper if val_upper in {'MIN', 'MAX', 'DEF'} else value
        elif not isinstance(value, (float, int)):
            raise ValueError("value must be float or one of 'MIN', 'MAX', 'DEF'")

        self.inst.write(f"SENSe:CURRent:{ac_dc}:NULL:VALue {value}")

    def get_current_null_value(self, ac_dc, query_type=None):
        """
        Query null value for AC or DC current.

        Args:
            ac_dc (str): 'AC' or 'DC'.
            query_type (str|None): Optional 'MIN', 'MAX', 'DEF'.

        Returns:
            str: Null value.
        """
        ac_dc = ac_dc.upper()
        if ac_dc not in {'AC', 'DC'}:
            raise ValueError("ac_dc must be 'AC' or 'DC'")

        if query_type:
            query_type = query_type.strip().upper()
            if query_type not in {'MIN', 'MAX', 'DEF'}:
                raise ValueError("query_type must be 'MIN', 'MAX', or 'DEF'")
            response = self.inst.query(f"SENSe:CURRent:{ac_dc}:NULL:VALue? {query_type}")
        else:
            response = self.inst.query(f"SENSe:CURRent:{ac_dc}:NULL:VALue?")
        return response.strip()

    # ---------------------------
    # Current Null Value Auto
    # ---------------------------
    def set_current_null_value_auto(self, ac_dc, state):
        """
        Enable or disable automatic null value for AC or DC current.

        Args:
            ac_dc (str): 'AC' or 'DC'.
            state (str): 'ON' or 'OFF'.

        Raises:
            ValueError: If invalid inputs.
        """
        ac_dc = ac_dc.upper()
        state = state.upper()
        if ac_dc not in {'AC', 'DC'}:
            raise ValueError("ac_dc must be 'AC' or 'DC'")
        if state not in {'ON', 'OFF'}:
            raise ValueError("state must be 'ON' or 'OFF'")
        self.inst.write(f"SENSe:CURRent:{ac_dc}:NULL:VALue:AUTO {state}")

    def get_current_null_value_auto(self, ac_dc):
        """
        Query automatic null value state for AC or DC current.

        Args:
            ac_dc (str): 'AC' or 'DC'.

        Returns:
            str: 'ON' or 'OFF'.
        """
        ac_dc = ac_dc.upper()
        if ac_dc not in {'AC', 'DC'}:
            raise ValueError("ac_dc must be 'AC' or 'DC'")
        return self.inst.query(f"SENSe:CURRent:{ac_dc}:NULL:VALue:AUTO?").strip()

    # ---------------------------
    # Current Range and Autorange
    # ---------------------------
    def set_current_range(self, ac_dc, value):
        """
        Set fixed current measurement range.

        Args:
            ac_dc (str): 'AC' or 'DC'.
            value (float|str): Numeric range or 'MIN', 'MAX', 'DEF'.

        Raises:
            ValueError: If invalid inputs.
        """
        ac_dc = ac_dc.upper()
        if ac_dc not in {'AC', 'DC'}:
            raise ValueError("ac_dc must be 'AC' or 'DC'")

        if isinstance(value, str):
            val_upper = value.strip().upper()
            if val_upper not in {'MIN', 'MAX', 'DEF'}:
                try:
                    float(value)
                except ValueError:
                    raise ValueError("value must be float or one of 'MIN', 'MAX', 'DEF'")
            value = val_upper if val_upper in {'MIN', 'MAX', 'DEF'} else value
        elif not isinstance(value, (float, int)):
            raise ValueError("value must be float or one of 'MIN', 'MAX', 'DEF'")

        self.inst.write(f"SENSe:CURRent:{ac_dc}:RANGe {value}")

    def get_current_range(self, ac_dc, query_type=None):
        """
        Query current measurement range.

        Args:
            ac_dc (str): 'AC' or 'DC'.
            query_type (str|None): Optional 'MIN', 'MAX', 'DEF'.

        Returns:
            str: Current range.
        """
        ac_dc = ac_dc.upper()
        if ac_dc not in {'AC', 'DC'}:
            raise ValueError("ac_dc must be 'AC' or 'DC'")

        if query_type:
            query_type = query_type.strip().upper()
            if query_type not in {'MIN', 'MAX', 'DEF'}:
                raise ValueError("query_type must be 'MIN', 'MAX', or 'DEF'")
            response = self.inst.query(f"SENSe:CURRent:{ac_dc}:RANGe? {query_type}")
        else:
            response = self.inst.query(f"SENSe:CURRent:{ac_dc}:RANGe?")
        return response.strip()

    def set_current_range_auto(self, ac_dc, state):
        """
        Enable or disable autorange for AC or DC current.

        Args:
            ac_dc (str): 'AC' or 'DC'.
            state (str): 'OFF', 'ON', or 'ONCE'.

        Raises:
            ValueError: If invalid inputs.
        """
        ac_dc = ac_dc.upper()
        state = state.upper()
        if ac_dc not in {'AC', 'DC'}:
            raise ValueError("ac_dc must be 'AC' or 'DC'")
        if state not in {'OFF', 'ON', 'ONCE'}:
            raise ValueError("state must be 'OFF', 'ON', or 'ONCE'")
        self.inst.write(f"SENSe:CURRent:{ac_dc}:RANGe:AUTO {state}")

    def get_current_range_auto(self, ac_dc):
        """
        Query autorange state for AC or DC current.

        Args:
            ac_dc (str): 'AC' or 'DC'.

        Returns:
            str: 'OFF', 'ON', or 'ONCE'.
        """
        ac_dc = ac_dc.upper()
        if ac_dc not in {'AC', 'DC'}:
            raise ValueError("ac_dc must be 'AC' or 'DC'")
        return self.inst.query(f"SENSe:CURRent:{ac_dc}:RANGe:AUTO?").strip()

    # ---------------------------
    # Current Terminals
    # ---------------------------
    def set_current_terminals(self, ac_dc, terminals):
        """
        Set current measurement terminals.

        Args:
            ac_dc (str): 'AC' or 'DC'.
            terminals (int): 3 or 10.

        Raises:
            ValueError: If invalid inputs.
        """
        ac_dc = ac_dc.upper()
        if ac_dc not in {'AC', 'DC'}:
            raise ValueError("ac_dc must be 'AC' or 'DC'")
        if terminals not in {3, 10}:
            raise ValueError("terminals must be 3 or 10")
        self.inst.write(f"SENSe:CURRent:{ac_dc}:TERMinals {terminals}")

    def get_current_terminals(self, ac_dc):
        """
        Query current measurement terminals.

        Args:
            ac_dc (str): 'AC' or 'DC'.

        Returns:
            str: '3' or '10'.
        """
        ac_dc = ac_dc.upper()
        if ac_dc not in {'AC', 'DC'}:
            raise ValueError("ac_dc must be 'AC' or 'DC'")
        return self.inst.query(f"SENSe:CURRent:{ac_dc}:TERMinals?").strip()

    # ---------------------------
    # AC Current Secondary Function
    # ---------------------------
    def set_current_ac_secondary(self, function):
        """
        Set AC current secondary function.

        Args:
            function (str): One of 'OFF', 'CALCulate:DATA', 'FREQuency', 'CURRent[:DC]'.

        Raises:
            ValueError: If invalid function.
        """
        valid_functions = {'OFF', 'CALCulate:DATA', 'FREQuency', 'CURRENT', 'CURR:DC', 'CURR:DC'}
        func_upper = function.strip().upper()
        # Normalize common variants
        if func_upper == 'CURRENT[:DC]':
            func_upper = 'CURR:DC'
        if func_upper not in {f.upper() for f in valid_functions}:
            raise ValueError(f"Invalid AC secondary function. Valid: {valid_functions}")
        self.inst.write(f'SENSe:CURRent:AC:SECondary "{function}"')

    def get_current_ac_secondary(self):
        """
        Query AC current secondary function.

        Returns:
            str: Secondary function string.
        """
        return self.inst.query("SENSe:CURRent:AC:SECondary?").strip()

    # ---------------------------
    # DC Current Aperture Time
    # ---------------------------
    def set_current_dc_aperture(self, value):
        """
        Set DC current aperture time (integration time).

        Args:
            value (float|str): Aperture time in seconds or 'MIN', 'MAX', 'DEF'.

        Raises:
            ValueError: If invalid.
        """
        valid_keywords = {'MIN', 'MAX', 'DEF'}
        if isinstance(value, str):
            val_upper = value.strip().upper()
            if val_upper not in valid_keywords:
                try:
                    val_float = float(value)
                    if not (0.00002 <= val_float <= 1):
                        raise ValueError
                except Exception:
                    raise ValueError("Invalid aperture time string")
            self.inst.write(f"SENSe:CURRent:DC:APERture {value}")
        elif isinstance(value, (float, int)):
            if not (0.00002 <= value <= 1):
                raise ValueError("Aperture time must be between 20 μs and 1 s")
            self.inst.write(f"SENSe:CURRent:DC:APERture {value}")
        else:
            raise ValueError("Aperture time must be float, int, or 'MIN', 'MAX', 'DEF'")

        # Enable aperture mode automatically
        self.set_current_dc_aperture_enabled('ON')

    def get_current_dc_aperture(self, query_type=None):
        """
        Query DC current aperture time.

        Args:
            query_type (str|None): Optional 'MIN', 'MAX', 'DEF'.

        Returns:
            str: Aperture time.
        """
        if query_type:
            query_type = query_type.strip().upper()
            if query_type not in {'MIN', 'MAX', 'DEF'}:
                raise ValueError("query_type must be 'MIN', 'MAX', or 'DEF'")
            response = self.inst.query(f"SENSe:CURRent:DC:APERture? {query_type}")
        else:
            response = self.inst.query("SENSe:CURRent:DC:APERture?")
        return response.strip()

    def set_current_dc_aperture_enabled(self, state):
        """
        Enable or disable DC current aperture mode.

        Args:
            state (str|int): 'ON', 'OFF', 1, or 0.

        Raises:
            ValueError: If invalid.
        """
        if isinstance(state, str):
            st = state.strip().upper()
            if st in {'ON', '1'}:
                val = 'ON'
            elif st in {'OFF', '0'}:
                val = 'OFF'
            else:
                raise ValueError("state must be 'ON', 'OFF', 1, or 0")
        elif isinstance(state, int):
            if state == 1:
                val = 'ON'
            elif state == 0:
                val = 'OFF'
            else:
                raise ValueError("state must be 'ON', 'OFF', 1, or 0")
        else:
            raise ValueError("state must be string or int")
        self.inst.write(f"SENSe:CURRent:DC:APERture:ENABled {val}")

    def get_current_dc_aperture_enabled(self):
        """
        Query DC current aperture enable state.

        Returns:
            str: 'ON' or 'OFF'.
        """
        resp = self.inst.query("SENSe:CURRent:DC:APERture:ENABled?")
        val = resp.strip()
        if val in {'1', 'ON'}:
            return 'ON'
        elif val in {'0', 'OFF'}:
            return 'OFF'
        else:
            return val

    # ---------------------------
    # DC Current NPLC
    # ---------------------------
    def set_current_dc_nplc(self, value):
        """
        Set DC current NPLC (power line cycles).

        Args:
            value (float|str): NPLC value or 'MIN', 'MAX', 'DEF'.

        Raises:
            ValueError: If invalid.
        """
        valid_keywords = {'MIN', 'MAX', 'DEF'}
        if isinstance(value, str):
            val_upper = value.strip().upper()
            if val_upper not in valid_keywords:
                try:
                    float(value)
                except Exception:
                    raise ValueError("Invalid NPLC string")
            self.inst.write(f"SENSe:CURRent:DC:NPLC {value}")
        elif isinstance(value, (float, int)):
            if value <= 0:
                raise ValueError("NPLC must be positive")
            self.inst.write(f"SENSe:CURRent:DC:NPLC {value}")
        else:
            raise ValueError("NPLC must be float, int, or 'MIN', 'MAX', 'DEF'")

    def get_current_dc_nplc(self, query_type=None):
        """
        Query DC current NPLC.

        Args:
            query_type (str|None): Optional 'MIN', 'MAX', 'DEF'.

        Returns:
            str: NPLC value.
        """
        if query_type:
            query_type = query_type.strip().upper()
            if query_type not in {'MIN', 'MAX', 'DEF'}:
                raise ValueError("query_type must be 'MIN', 'MAX', or 'DEF'")
            response = self.inst.query(f"SENSe:CURRent:DC:NPLC? {query_type}")
        else:
            response = self.inst.query("SENSe:CURRent:DC:NPLC?")
        return response.strip()

    # ---------------------------
    # DC Current Resolution
    # ---------------------------
    def set_current_dc_resolution(self, value):
        """
        Set DC current resolution.

        Args:
            value (float|str): Resolution value or 'MIN', 'MAX', 'DEF'.

        Raises:
            ValueError: If invalid.
        """
        valid_keywords = {'MIN', 'MAX', 'DEF'}
        if isinstance(value, str):
            val_upper = value.strip().upper()
            if val_upper not in valid_keywords:
                try:
                    float(value)
                except Exception:
                    raise ValueError("Invalid resolution string")
            self.inst.write(f"SENSe:CURRent:DC:RESolution {value}")
        elif isinstance(value, (float, int)):
            if value <= 0:
                raise ValueError("Resolution must be positive")
            self.inst.write(f"SENSe:CURRent:DC:RESolution {value}")
        else:
            raise ValueError("Resolution must be float, int, or 'MIN', 'MAX', 'DEF'")

    def get_current_dc_resolution(self, query_type=None):
        """
        Query DC current resolution.

        Args:
            query_type (str|None): Optional 'MIN', 'MAX', 'DEF'.

        Returns:
            str: Resolution value.
        """
        if query_type:
            query_type = query_type.strip().upper()
            if query_type not in {'MIN', 'MAX', 'DEF'}:
                raise ValueError("query_type must be 'MIN', 'MAX', or 'DEF'")
            response = self.inst.query(f"SENSe:CURRent:DC:RESolution? {query_type}")
        else:
            response = self.inst.query("SENSe:CURRent:DC:RESolution?")
        return response.strip()

    # ---------------------------
    # DC Current Secondary Function
    # ---------------------------
    def set_current_dc_secondary(self, function):
        """
        Set DC current secondary function.

        Args:
            function (str): One of 'OFF', 'CALCulate:DATA', 'CURRent:AC', 'PTPeak'.

        Raises:
            ValueError: If invalid.
        """
        valid_functions = {'OFF', 'CALCulate:DATA', 'CURRent:AC', 'PTPeak'}
        func_upper = function.strip().upper()
        if func_upper not in {f.upper() for f in valid_functions}:
            raise ValueError(f"Invalid DC secondary function. Valid: {valid_functions}")
        self.inst.write(f'SENSe:CURRent:DC:SECondary "{function}"')

    def get_current_dc_secondary(self):
        """
        Query DC current secondary function.

        Returns:
            str: Secondary function string.
        """
        return self.inst.query("SENSe:CURRent:DC:SECondary?").strip()

    # ---------------------------
    # DC Current Zero Auto
    # ---------------------------
    def set_current_dc_zero_auto(self, state):
        """
        Set DC current zero auto mode.

        Args:
            state (str): 'OFF', 'ON', or 'ONCE'.

        Raises:
            ValueError: If invalid.
        """
        state = state.upper()
        if state not in {'OFF', 'ON', 'ONCE'}:
            raise ValueError("state must be 'OFF', 'ON', or 'ONCE'")
        self.inst.write(f"SENSe:CURRent:DC:ZERO:AUTO {state}")

    def get_current_dc_zero_auto(self):
        """
        Query DC current zero auto mode.

        Returns:
            str: 'OFF', 'ON', or 'ONCE'.
        """
        return self.inst.query("SENSe:CURRent:DC:ZERO:AUTO?").strip()

    # ---------------------------
    # Current Switch Mode
    # ---------------------------
    def set_current_switch_mode(self, mode):
        """
        Set current switch mode.

        Args:
            mode (str): 'FAST' or 'CONTinuous'.

        Raises:
            ValueError: If invalid.
        """
        mode_upper = mode.upper()
        if mode_upper not in {'FAST', 'CONTINUOUS'}:
            raise ValueError("mode must be 'FAST' or 'CONTinuous'")
        self.inst.write(f"SENSe:CURRent:SWITch:MODE {mode_upper}")

    def get_current_switch_mode(self):
        """
        Query current switch mode.

        Returns:
            str: 'FAST' or 'CONTinuous'.
        """
        return self.inst.query("SENSe:CURRent:SWITch:MODE?").strip()

    # ---------------------------
    # Close instrument connection
    # ---------------------------
    def close(self):
        self.inst.close()
        self.rm.close()