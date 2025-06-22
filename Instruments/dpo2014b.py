import time
import pyvisa
import numpy as np
from scipy import signal

class DPO2014B:
    """
    Tektronix DPO2014B Digital Oscilloscope SCPI Control Class.

    This class provides comprehensive control over the Tektronix DPO2014B oscilloscope using SCPI commands.
    It covers:
    - Basic instrument control (IDN, reset, status)
    - Channel configuration (display, scale, position, coupling)
    - Timebase configuration
    - Trigger setup and monitoring (including extended trigger A lower threshold and mode)
    - Measurements (voltage, time, frequency, etc.)
    - Math functions (FFT, add, subtract, etc.)
    - Waveform acquisition and data retrieval
    - Screen image capture
    - Initialization and application-level functions
    """

    def __init__(self, resource_name):
        self.rm = pyvisa.ResourceManager()
        self.inst = self.rm.open_resource(resource_name)
        self.inst.timeout = 15000  # 15 seconds timeout for long operations
        self.inst.read_termination = '\n'
        self.inst.write_termination = '\n'

    # ---------------------------
    # 1. Basic Instrument Control
    # ---------------------------

    def identify(self):
        return self.inst.query("*IDN?").strip()

    def reset(self):
        self.inst.write("*RST")
        time.sleep(2)

    def clear_status(self):
        self.inst.write("*CLS")

    def self_test(self):
        return self.inst.query("*TST?").strip()

    def get_error(self):
        return self.inst.query("SYST:ERR?").strip()

    # ---------------------------
    # 2. Channel Configuration
    # ---------------------------

    def set_channel_display(self, channel:int, state:bool):
        val = 'ON' if state else 'OFF'
        self.inst.write(f"CHAN{channel}:DISP {val}")

    def get_channel_display(self, channel:int):
        return self.inst.query(f"CHAN{channel}:DISP?").strip()

    def set_channel_scale(self, channel:int, volts_per_div:float):
        self.inst.write(f"CHAN{channel}:SCAL {volts_per_div}")

    def get_channel_scale(self, channel:int):
        return float(self.inst.query(f"CHAN{channel}:SCAL?"))

    def set_channel_position(self, channel:int, position_volts:float):
        self.inst.write(f"CHAN{channel}:POS {position_volts}")

    def get_channel_position(self, channel:int):
        return float(self.inst.query(f"CHAN{channel}:POS?"))

    def set_channel_coupling(self, channel:int, coupling:str):
        coupling = coupling.upper()
        if coupling not in ['DC', 'AC', 'GND']:
            raise ValueError("Coupling must be 'DC', 'AC', or 'GND'")
        self.inst.write(f"CHAN{channel}:COUP {coupling}")

    def get_channel_coupling(self, channel:int):
        return self.inst.query(f"CHAN{channel}:COUP?").strip()

    def set_channel_bandwidth_limit(self, channel:int, enable:bool):
        val = 'ON' if enable else 'OFF'
        self.inst.write(f"CHAN{channel}:BWLIM {val}")

    def get_channel_bandwidth_limit(self, channel:int):
        return self.inst.query(f"CHAN{channel}:BWLIM?").strip()
    
    def set_channel(self, channel, display=True, scale=1.0, position=0.0, coupling='DC'):
        self.scope.write(f"CHAN{channel}:DISP {'ON' if display else 'OFF'}")
        self.scope.write(f"CHAN{channel}:SCAL {scale}")
        self.scope.write(f"CHAN{channel}:POS {position}")
        self.scope.write(f"CHAN{channel}:COUP {coupling}")
    # ---------------------------
    # 3. Timebase Configuration
    # ---------------------------

    def set_timebase_scale(self, seconds_per_div:float):
        self.inst.write(f"HOR:MAIN:SCA {seconds_per_div}")

    def get_timebase_scale(self):
        return float(self.inst.query("HOR:MAIN:SCA?"))

    def set_timebase_position(self, seconds:float):
        self.inst.write(f"HOR:MAIN:POS {seconds}")

    def get_timebase_position(self):
        return float(self.inst.query("HOR:MAIN:POS?"))

    def set_timebase_reference(self, reference:str):
        reference = reference.upper()
        if reference not in ['LEFT', 'CENTER', 'RIGHT']:
            raise ValueError("Reference must be 'LEFT', 'CENTER', or 'RIGHT'")
        self.inst.write(f"HOR:MAIN:REF {reference}")

    def get_timebase_reference(self):
        return self.inst.query("HOR:MAIN:REF?").strip()

    # ---------------------------
    # 4. Trigger Setup and Monitor
    # ---------------------------

    def set_trigger_mode(self, mode:str):
        mode = mode.upper()
        valid_modes = ['EDGE', 'PULSE', 'VIDEO', 'SLOPE', 'RUNT', 'WINDOW', 'GLITCH', 'TV', 'PATTERN', 'STATE']
        if mode not in valid_modes:
            raise ValueError(f"Invalid trigger mode. Valid options: {valid_modes}")
        self.inst.write(f"TRIG:MODE {mode}")

    def get_trigger_mode(self):
        return self.inst.query("TRIG:MODE?").strip()

    def set_trigger_edge_source(self, channel:int):
        self.inst.write(f"TRIG:EDGE:SOURCE CHAN{channel}")

    def get_trigger_edge_source(self):
        return self.inst.query("TRIG:EDGE:SOURCE?").strip()

    def set_trigger_edge_slope(self, slope:str):
        slope = slope.upper()
        if slope not in ['POS', 'NEG', 'EITH']:
            raise ValueError("Slope must be 'POS', 'NEG', or 'EITH'")
        self.inst.write(f"TRIG:EDGE:SLOP {slope}")

    def get_trigger_edge_slope(self):
        return self.inst.query("TRIG:EDGE:SLOP?").strip()

    def set_trigger_level(self, channel:int, level_volts:float):
        self.inst.write(f"TRIG:EDGE:LEV CHAN{channel},{level_volts}")

    def get_trigger_level(self, channel:int):
        return float(self.inst.query(f"TRIG:EDGE:LEV? CHAN{channel}"))

    def get_trigger_status(self):
        return self.inst.query("TRIG:STAT?").strip()

    def is_triggered(self):
        status = self.get_trigger_status()
        return status in ['TD', 'ARM', 'STOP']

    # --- Added Trigger A Lower Threshold and Mode commands ---

    def set_trigger_a_lower_threshold(self, level, source='EXT'):
        """
        Sets the lower threshold for the Auxiliary Input trigger.
        SCPI: TRIGger:A:LOWerthreshold{:EXT|:AUX} {<NR3>|ECL|TTL}
        """
        source = source.upper()
        if source not in ['EXT', 'AUX']:
            raise ValueError("Source must be 'EXT' or 'AUX'")

        if isinstance(level, str):
            level = level.upper()
            if level not in ['ECL', 'TTL']:
                raise ValueError("Level string must be 'ECL' or 'TTL'")
            cmd = f"TRIGger:A:LOWerthreshold:{source} {level}"
        else:
            cmd = f"TRIGger:A:LOWerthreshold:{source} {float(level)}"
        self.inst.write(cmd)

    def query_trigger_a_lower_threshold(self, source='EXT'):
        """
        Queries the lower threshold for the Auxiliary Input trigger.
        SCPI: TRIGger:A:LOWerthreshold{:EXT|:AUX}?
        """
        source = source.upper()
        if source not in ['EXT', 'AUX']:
            raise ValueError("Source must be 'EXT' or 'AUX'")

        cmd = f"TRIGger:A:LOWerthreshold:{source}?"
        return self.inst.query(cmd).strip()

    def set_trigger_a_mode(self, mode):
        """
        Sets the A trigger mode.
        SCPI: TRIGger:A:MODe {AUTO|NORMal}
        """
        mode = mode.upper()
        if mode not in ['AUTO', 'NORMAL']:
            raise ValueError("Mode must be 'AUTO' or 'NORMAL'")
        self.inst.write(f"TRIGger:A:MODe {mode}")

    def query_trigger_a_mode(self):
        """
        Queries the A trigger mode.
        SCPI: TRIGger:A:MODe?
        """
        return self.inst.query("TRIGger:A:MODe?").strip()

    # ---------------------------
    # 5. Measurement Functions
    # ---------------------------

    def enable_measurement(self, meas_num:int, meas_type:str, channel:int):
        self.inst.write(f"MEASU:MEAS{meas_num}:TYPE {meas_type}")
        self.inst.write(f"MEASU:MEAS{meas_num}:SOURCE CHAN{channel}")
        self.inst.write(f"MEASU:MEAS{meas_num}:STATE ON")

    def disable_measurement(self, meas_num:int):
        self.inst.write(f"MEASU:MEAS{meas_num}:STATE OFF")

    def query_measurement(self, meas_num:int):
        return float(self.inst.query(f"MEASU:MEAS{meas_num}:VAL?"))

    # ---------------------------
    # 6. Math Functions
    # ---------------------------

    def enable_math_function(self, func:str):
        func = func.upper()
        valid_funcs = ['ADD', 'SUB', 'MUL', 'DIV', 'FFT', 'INV', 'SQRT', 'LOG', 'EXP', 'ABS']
        if func not in valid_funcs:
            raise ValueError(f"Invalid math function. Valid options: {valid_funcs}")
        self.inst.write(f"MATH:FUNC {func}")
        self.inst.write("MATH:STATE ON")

    def disable_math(self):
        self.inst.write("MATH:STATE OFF")

    def set_math_source(self, source1:str, source2:str=None):
        self.inst.write(f"MATH:SOU1 {source1}")
        if source2:
            self.inst.write(f"MATH:SOU2 {source2}")

    # ---------------------------
    # 7. Waveform Acquisition and Data Retrieval
    # ---------------------------

    def run_acquisition(self):
        self.inst.write("ACQ:STATE RUN")

    def stop_acquisition(self):
        self.inst.write("ACQ:STATE STOP")

    def fetch_waveform_raw(self, channel:int):
        self.inst.write(f"DATA:SOURCE CH{channel}")
        self.inst.write("DATA:WIDTH 1")
        self.inst.write("DATA:ENC RPB")
        raw_data = self.inst.query_binary_values("CURVE?", datatype='b', container=list)
        return raw_data

    def fetch_waveform(self, channel:int):
        """
        Fetch waveform and convert to voltage/time arrays using preamble info.
        """
        self.inst.write(f"DATA:SOURCE CH{channel}")
        preamble = self.inst.query("WFMPRE?").strip().split(';')
        # Parse preamble fields (example: format, type, points, xIncrement, xOrigin, yIncrement, yOrigin, yReference)
        # For brevity, parse key fields only:
        x_increment = float(self._get_preamble_value(preamble, 'XINCR'))
        x_origin = float(self._get_preamble_value(preamble, 'XORIG'))
        y_increment = float(self._get_preamble_value(preamble, 'YINCR'))
        y_origin = float(self._get_preamble_value(preamble, 'YORIG'))
        y_reference = float(self._get_preamble_value(preamble, 'YREF'))

        raw_data = self.fetch_waveform_raw(channel)
        voltages = [(y - y_reference) * y_increment + y_origin for y in raw_data]
        times = [x_origin + i * x_increment for i in range(len(raw_data))]
        return times, voltages

    def _get_preamble_value(self, preamble_list, key):
        for item in preamble_list:
            if item.startswith(key):
                return item.split(' ')[1]
        raise ValueError(f"Preamble key {key} not found")

    # ---------------------------
    # 8. Screen Image Capture
    # ---------------------------

    def capture_screen_image(self, filename:str = "screen_capture.png", image_format:str = "PNG"):
        image_format = image_format.upper()
        valid_formats = ['PNG', 'BMP', 'JPEG', 'TIFF']
        if image_format not in valid_formats:
            raise ValueError(f"Invalid image format. Valid options: {valid_formats}")

        self.inst.write(f"HARDcopy:FORMat {image_format}")
        self.inst.write("HARDcopy START")
        time.sleep(2)

        img_data = self.inst.query_binary_values("MMEM:DATA? 'C:\\screen_capture.png'", datatype='B', container=bytearray)
        with open(filename, 'wb') as f:
            f.write(img_data)
        print(f"Screen image saved to {filename}")
# ---------------------------
    # Data Export Helpers
    # ---------------------------

    def export_waveform_to_csv(self, times, voltages, filename="waveform.csv"):
        import csv
        with open(filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Time (s)', 'Voltage (V)'])
            for t, v in zip(times, voltages):
                writer.writerow([t, v])
        print(f"Waveform data exported to {filename}")

    def export_waveform_to_json(self, times, voltages, filename="waveform.json"):
        import json
        data = [{'time': t, 'voltage': v} for t, v in zip(times, voltages)]
        with open(filename, 'w') as jsonfile:
            json.dump(data, jsonfile, indent=4)
        print(f"Waveform data exported to {filename}")

    # ---------------------------
    # Application-Level Examples
    # ---------------------------

    def basic_capture_and_export(self, channel=1, csv_file="waveform.csv"):
        self.run_acquisition()
        time.sleep(1)
        self.stop_acquisition()
        times, volts = self.fetch_waveform(channel)
        self.export_waveform_to_csv(times, volts, csv_file)
        return times, volts

    def fft_analysis(self, channel=1):
        times, volts = self.fetch_waveform(channel)
        fs = 1 / (times[1] - times[0])
        f, Pxx = signal.welch(volts, fs)
        return f, Pxx
    # ---------------------------
    # 9. Initialization and Utility Functions
    # ---------------------------

    def initialize(self):
        self.reset()
        time.sleep(2)
        self.clear_status()

        for ch in range(1, 5):
            self.set_channel_display(ch, False)
        self.set_channel_display(1, True)
        self.set_channel_scale(1, 1.0)
        self.set_channel_position(1, 0.0)
        self.set_channel_coupling(1, 'DC')

        self.set_timebase_scale(1e-3)
        self.set_timebase_position(0.0)
        self.set_trigger_mode('EDGE')
        self.set_trigger_edge_source(1)
        self.set_trigger_edge_slope('POS')
        self.set_trigger_level(1, 0.0)

    # ---------------------------
    # 10. Application-Level Functions
    # ---------------------------

    def wait_for_trigger(self, timeout_sec=10,sleep_interval=0.1):
        start_time = time.time()
        while time.time() - start_time < timeout_sec:
            if self.is_triggered():
                return True
            time.sleep(sleep_interval)
        return False

    def capture_waveform_on_trigger(self, channel:int=1, timeout_sec=10):
        self.run_acquisition()
        triggered = self.wait_for_trigger(timeout_sec)
        self.stop_acquisition()
        if triggered:
            return self.fetch_waveform(channel)
        else:
            print("Trigger timeout expired.")
            return None

    # ---------------------------
    # Close Connection
    # ---------------------------

    def close(self):
        self.inst.close()
        self.rm.close()
