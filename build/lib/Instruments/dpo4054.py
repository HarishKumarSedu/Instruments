import time
import pyvisa
import numpy as np
import csv
import json

class DPO4054:
    """
    Tektronix DPO4054 Oscilloscope SCPI Control Class (per Programmer Manual 077-0248-01).
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
        if slope not in ['RISE', 'FALL', 'EITH']:
            raise ValueError("Slope must be 'RISE', 'FALL', or 'EITH'")
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
    
    def autoset_and_wait(self, timeout=10):
        """Perform autoset and wait for completion."""
        self.inst.write("AUTOS EXECute")
        start = time.time()
        while time.time() - start < timeout:
            if self.inst.query("*OPC?").strip() == "1":
                return True
            time.sleep(0.2)
        raise TimeoutError("Autoset did not complete in time.")

    def wait_for_acquisition_complete(self, timeout=10):
        """Wait until acquisition completes (single sequence)."""
        start = time.time()
        while time.time() - start < timeout:
            if self.inst.query("BUSY?").strip() == "0":
                return True
            time.sleep(0.1)
        raise TimeoutError("Acquisition did not complete in time.")

    def single_sequence_then_live(self, timeout=10, sampling_interval=0.1):
        """
        Run a single acquisition, wait for trigger, then return to normal live (auto/roll) mode.

        Args:
            timeout (float): Maximum time to wait for the single acquisition (seconds).
            sampling_interval (float): Time between BUSY? status checks (seconds).
        """
        # 1. Set single sequence mode
        self.inst.write("ACQuire:STOPAfter SEQ")
        self.inst.write("ACQuire:STATE RUN")

        # 2. Wait for acquisition to complete (BUSY? returns '0' when done)
        start = time.time()
        while time.time() - start < timeout:
            try:
                if self.inst.query("BUSY?").strip() == "0":
                    break
            except Exception:
                pass
            time.sleep(sampling_interval)
        else:
            raise TimeoutError("Single sequence did not complete in time.")

        # 3. Set back to continuous (auto/roll) mode
        self.inst.write("ACQuire:STOPAfter RUNST")  # or "RUNT" depending on firmware
        self.inst.write("ACQuire:STATE RUN")


    def save_setup(self, filename="setup.stp"):
        """Save the current oscilloscope setup to internal memory."""
        self.inst.write(f"SAVE:SETUP \"{filename}\"")

    def recall_setup(self, filename="setup.stp"):
        """Recall a saved oscilloscope setup from internal memory."""
        self.inst.write(f"RECALL:SETUP \"{filename}\"")

    def clear_all_measurements(self):
        """Clear all automatic measurements."""
        self.inst.write("MEASU:CLEar")

    def add_measurement(self, meas_type, source):
        """Add a measurement (e.g., 'FREQ', 'PK2PK', 'MEAN') on a given source."""
        self.inst.write(f"MEASU:ADDMeas {meas_type},{source}")

    def get_all_measurements(self):
        """Return all current measurement values as a dictionary."""
        results = {}
        for i in range(1, 9):  # DPO4054 supports up to 8 measurements
            try:
                val = float(self.inst.query(f"MEASU:MEAS{i}:VAL?"))
                results[f"MEAS{i}"] = val
            except Exception:
                continue
        return results

    def get_channel_stats(self, channel):
        """Return mean, min, max, and stddev for a channel's waveform."""
        self.inst.write(f"DATA:SOU CH{channel}")
        data = np.array(self.fetch_waveform_raw(channel))
        return {
            "mean": float(np.mean(data)),
            "min": float(np.min(data)),
            "max": float(np.max(data)),
            "std": float(np.std(data))
        }

    def save_screen_image(self, filename="screen.png", img_format="PNG", scope_path="C:/Temp/screen.png"):
       """
       Save the oscilloscope screen image to a file on the PC.
       Args:
           filename: Name for the file on the PC.
           img_format: One of 'PNG', 'BMP', 'TIFF', 'JPEG'.
           scope_path: Path/filename on the oscilloscope's internal memory.
       """
       img_format = img_format.upper()
       valid_formats = ['PNG', 'BMP', 'TIFF', 'JPEG']
       if img_format not in valid_formats:
           raise ValueError(f"Invalid image format. Valid options: {valid_formats}")    
       # Set the image format
       self.inst.write(f"HARDCopy:FORMat {img_format}") 
       # Set destination to file and specify filename
       self.inst.write("HARDCopy:DEST 'FILE'")
       self.inst.write(f"HARDCopy:FILEName '{scope_path}'") 
       # Start hardcopy, then wait for completion
       self.inst.write("HARDCopy STARt")
       self.inst.query("*OPC?")  # Wait for operation complete  
       # Now fetch the file from scope's memory
       img_data = self.inst.query_binary_values(f"MMEMory:DATA? '{scope_path}'", datatype='B', container=bytearray) 
       # Save to PC
       with open(filename, 'wb') as f:
           f.write(img_data)    
       # Optionally, delete the file from the scope
       # self.inst.write(f"FILESystem:DELete '{scope_path}'")



    def export_all_waveforms_csv(self, filename_prefix="waveform"):
        """Export all displayed channels to CSV files."""
        for ch in range(1, 5):
            # Only export if channel is displayed (track in software or assume ON)
            times, volts = self.fetch_waveform(ch)
            fname = f"{filename_prefix}_ch{ch}.csv"
            self.export_waveform_to_csv(times, volts, fname)

    def measure_and_save(self, channel, meas_types, filename="meas_results.json"):
        """Perform a list of measurements on a channel and save results to JSON."""
        self.clear_all_measurements()
        results = {}
        for i, mtype in enumerate(meas_types, 1):
            self.add_measurement(mtype, f"CH{channel}")
            time.sleep(0.1)
            val = float(self.inst.query(f"MEASU:MEAS{i}:VAL?"))
            results[mtype] = val
        with open(filename, "w") as f:
            json.dump(results, f, indent=2)
        return results

    def set_and_verify_channel_scale(self, channel, scale):
        """Set the channel scale and verify that it was set."""
        self.set_channel_scale(channel, scale)
        actual = self.get_channel_scale(channel)
        if abs(actual - scale) > 1e-6:
            raise ValueError(f"Scale mismatch: set {scale}, got {actual}")
        return actual

    def trigger_setup(self, channel, level, slope="RISE", mode="EDGE"):
        """Setup edge trigger robustly and verify."""
        self.set_trigger_mode(mode)
        self.set_trigger_edge_source(channel)
        self.set_trigger_edge_slope(slope)
        self.set_trigger_level(channel, level)
        # Verify
        assert self.get_trigger_mode() == mode
        assert self.get_trigger_edge_source() == f"CH{channel}"
        assert self.get_trigger_edge_slope() == slope
        assert abs(self.get_trigger_level(channel) - level) < 1e-3
    def setup_channel(self, channel, display=True, scale=1.0, position=0.0, coupling='DC', bandwidth_limit=False):
        """
        Configure a channel's display, scale, position, coupling, and bandwidth limit.
        """
        # Display ON/OFF
        val = 'ON' if display else 'OFF'
        self.inst.write(f"SELect:CH{channel} {val}")

        # Vertical scale (V/div)
        self.inst.write(f"CH{channel}:SCAle {scale}")

        # Vertical position (div)
        self.inst.write(f"CH{channel}:POSition {position}")

        # Coupling (DC, AC, GND)
        coupling = coupling.upper()
        if coupling not in ['DC', 'AC', 'GND']:
            raise ValueError("Coupling must be 'DC', 'AC', or 'GND'")
        self.inst.write(f"CH{channel}:COUPling {coupling}")

        # Bandwidth limit (ON/OFF)
        bw = 'ON' if bandwidth_limit else 'OFF'
        self.inst.write(f"CH{channel}:BWL {bw}")

    def setup_edge_trigger(self, source_channel=1, level=0.0, slope='RISE', mode='EDGE'):
        """
        Configure edge trigger: source channel, level, slope, and mode.
        """
        # Set trigger type
        self.inst.write(f"TRIGger:A:TYPe {mode}")

        # Set trigger source
        self.inst.write(f"TRIGger:A:EDGE:SOUrce CH{source_channel}")

        # Set trigger slope (RISE, FALL, EITH)
        slope = slope.upper()
        if slope not in ['RISE', 'FALL', 'EITH']:
            raise ValueError("Slope must be 'RISE', 'FALL', or 'EITH'")
        self.inst.write(f"TRIGger:A:EDGE:SLOpe {slope}")

        # Set trigger level (V)
        self.inst.write(f"TRIGger:A:LEVel:CH{source_channel} {level}")

    def setup_pulse_trigger(self, source_channel=1, level=0.0, width=1e-6, polarity='POS', condition='GREATER'):
        """
        Configure a pulse width trigger.
        """
        self.inst.write("TRIGger:A:TYPe WIDth")
        self.inst.write(f"TRIGger:A:WIDth:SOUrce CH{source_channel}")
        self.inst.write(f"TRIGger:A:LEVel:CH{source_channel} {level}")
        self.inst.write(f"TRIGger:A:WIDth:POLarity {polarity}")
        self.inst.write(f"TRIGger:A:WIDth:CONDition {condition}")
        self.inst.write(f"TRIGger:A:WIDth:WIDth {width}")

    def setup_video_trigger(self, source_channel=1, standard='NTSC', polarity='NEG'):
        """
        Configure a video trigger.
        """
        self.inst.write("TRIGger:A:TYPe TV")
        self.inst.write(f"TRIGger:A:TV:SOUrce CH{source_channel}")
        self.inst.write(f"TRIGger:A:TV:STANdard {standard}")
        self.inst.write(f"TRIGger:A:TV:POLarity {polarity}")

    def close(self):
        self.inst.close()
        self.rm.close()
