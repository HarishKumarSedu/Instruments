import time
import pyvisa
import numpy as np
import csv
import json

class MDO4034C:
    """
    Tektronix MDO4034C Oscilloscope SCPI Control Class (per Programmer Manual 077-0248-01).
    """

    def __init__(self, resource_name):
        self.rm = pyvisa.ResourceManager()
        self.inst = self.rm.open_resource(resource_name)
        self.inst.timeout = 15000
        self.inst.read_termination = '\n'
        self.inst.write_termination = '\n'

    # Basic Instrument Control

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
        return self.inst.query("ALLEV?").strip()

    # Channel (Vertical) Control

    def set_channel_display(self, channel:int, state:bool):
        val = 'ON' if state else 'OFF'
        self.inst.write(f"SELect:CH{channel} {val}")

    def set_channel_scale(self, channel:int, volts_per_div:float):
        self.inst.write(f"CH{channel}:SCAle {volts_per_div}")

    def get_channel_scale(self, channel:int):
        return float(self.inst.query(f"CH{channel}:SCAle?"))

    def set_channel_position(self, channel:int, position:float):
        self.inst.write(f"CH{channel}:POSition {position}")

    def get_channel_position(self, channel:int):
        return float(self.inst.query(f"CH{channel}:POSition?"))

    def set_channel_coupling(self, channel:int, coupling:str):
        coupling = coupling.upper()
        if coupling not in ['DC', 'AC', 'GND']:
            raise ValueError("Coupling must be 'DC', 'AC', or 'GND'")
        self.inst.write(f"CH{channel}:COUPling {coupling}")

    def get_channel_coupling(self, channel:int):
        return self.inst.query(f"CH{channel}:COUPling?").strip()

    def set_channel_bandwidth_limit(self, channel:int, enable:bool):
        val = 'ON' if enable else 'OFF'
        self.inst.write(f"CH{channel}:BWL {val}")

    def get_channel_bandwidth_limit(self, channel:int):
        return self.inst.query(f"CH{channel}:BWL?").strip()

    # Horizontal (Timebase) Control

    def set_timebase_scale(self, seconds_per_div:float):
        self.inst.write(f"HORizontal:MAIn:SCAle {seconds_per_div}")

    def get_timebase_scale(self):
        return float(self.inst.query("HORizontal:MAIn:SCAle?"))

    def set_timebase_position(self, seconds:float):
        self.inst.write(f"HORizontal:MAIn:POSition {seconds}")

    def get_timebase_position(self):
        return float(self.inst.query("HORizontal:MAIn:POSition?"))

    # Trigger Control

    def set_trigger_mode(self, mode:str):
        mode = mode.upper()
        valid_modes = ['EDGE', 'GLITch', 'WIDth', 'RUNT', 'WINDOW', 'TIMEOUT', 'TRANSITION', 'TV', 'PATTERN', 'STATE', 'SETUPHOLD']
        if mode not in valid_modes:
            raise ValueError(f"Invalid trigger mode. Valid options: {valid_modes}")
        self.inst.write(f"TRIGger:A:TYPe {mode}")

    def get_trigger_mode(self):
        return self.inst.query("TRIGger:A:TYPe?").strip()

    def set_trigger_edge_source(self, channel:int):
        self.inst.write(f"TRIGger:A:EDGE:SOUrce CH{channel}")

    def get_trigger_edge_source(self):
        return self.inst.query("TRIGger:A:EDGE:SOUrce?").strip()

    def set_trigger_edge_slope(self, slope:str):
        slope = slope.upper()
        if slope not in ['RIS', 'FALL', 'EITH']:
            raise ValueError("Slope must be 'RIS', 'FALL', or 'EITH'")
        self.inst.write(f"TRIGger:A:EDGE:SLOpe {slope}")

    def get_trigger_edge_slope(self):
        return self.inst.query("TRIGger:A:EDGE:SLOpe?").strip()

    def set_trigger_level(self, channel:int, level_volts:float):
        self.inst.write(f"TRIGger:A:LEVel:CH{channel} {level_volts}")

    def get_trigger_level(self, channel:int):
        return float(self.inst.query(f"TRIGger:A:LEVel:CH{channel}?"))

    def get_trigger_status(self):
        return self.inst.query("TRIGger:STATE?").strip()

    # Acquisition Control

    def run_acquisition(self):
        self.inst.write("ACQuire:STATE RUN")

    def stop_acquisition(self):
        self.inst.write("ACQuire:STATE STOP")

    # Measurement

    def add_measurement(self, meas_type:str, source:str):
        self.inst.write(f"MEASUrement:ADDMeas {meas_type},{source}")

    def clear_measurements(self):
        self.inst.write("MEASUrement:CLEar")

    def get_measurement_value(self, meas_num:int):
        return float(self.inst.query(f"MEASUrement:MEAS{meas_num}:VALue?"))

    # Math

    def enable_math(self, func:str):
        self.inst.write(f"MATH:DEFINE {func}")
        self.inst.write("MATH:STATE ON")

    def disable_math(self):
        self.inst.write("MATH:STATE OFF")

    # Waveform Data Transfer

    def fetch_waveform_raw(self, channel:int):
        self.inst.write(f"DATA:SOUrce CH{channel}")
        self.inst.write("DATA:WIDTH 1")
        self.inst.write("DATA:ENCdg RPB")
        return self.inst.query_binary_values("CURVe?", datatype='b', container=list)

    def fetch_waveform(self, channel:int):
        self.inst.write(f"DATA:SOUrce CH{channel}")
        preamble = self.inst.query("WFMPRE?").strip().split(';')
        x_increment = float(self._get_preamble_value(preamble, 'XINCR'))
        x_origin = float(self._get_preamble_value(preamble, 'XZERO'))
        y_increment = float(self._get_preamble_value(preamble, 'YMULT'))
        y_origin = float(self._get_preamble_value(preamble, 'YZERO'))
        y_reference = float(self._get_preamble_value(preamble, 'YOFF'))

        raw_data = self.fetch_waveform_raw(channel)
        voltages = [(y - y_reference) * y_increment + y_origin for y in raw_data]
        times = [x_origin + i * x_increment for i in range(len(raw_data))]
        return times, voltages

    def _get_preamble_value(self, preamble_list, key):
        for item in preamble_list:
            if item.startswith(key):
                return item.split(' ')[1]
        raise ValueError(f"Preamble key {key} not found")

    # Screen Capture

    def capture_screen_image(self, filename:str = "screen_capture.png", image_format:str = "PNG"):
        image_format = image_format.upper()
        valid_formats = ['PNG', 'BMP', 'JPEG', 'TIFF']
        if image_format not in valid_formats:
            raise ValueError(f"Invalid image format. Valid options: {valid_formats}")

        self.inst.write(f"HARDCopy:FORMat {image_format}")
        self.inst.write("HARDCopy STARt")
        time.sleep(2)
        img_data = self.inst.query_binary_values("MMEMory:DATA? 'C:\\screen_capture.png'", datatype='B', container=bytearray)
        with open(filename, 'wb') as f:
            f.write(img_data)
        print(f"Screen image saved to {filename}")

    # Data Export

    def export_waveform_to_csv(self, times, voltages, filename="waveform.csv"):
        with open(filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Time (s)', 'Voltage (V)'])
            for t, v in zip(times, voltages):
                writer.writerow([t, v])
        print(f"Waveform data exported to {filename}")

    def export_waveform_to_json(self, times, voltages, filename="waveform.json"):
        data = [{'time': t, 'voltage': v} for t, v in zip(times, voltages)]
        with open(filename, 'w') as jsonfile:
            json.dump(data, jsonfile, indent=4)
        print(f"Waveform data exported to {filename}")

    # Utility

    def close(self):
        self.inst.close()
        self.rm.close()
