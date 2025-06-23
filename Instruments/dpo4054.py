import time
import pyvisa
import numpy as np
import csv
import json
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.signal import find_peaks, windows

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

    def add_measurement(self, meas_type: str, channel: int,slot: int = 1,source: int = 1):
        """
        Adds a measurement of type `meas_type` on `channel` to the first available slot.
        Returns the slot number used.
        """
        self.inst.write(f"MEASUREMENT:MEAS{slot}:TYPE {meas_type.upper()}")
        self.inst.write(f"MEASUREMENT:MEAS{slot}:SOURCE{source} CH{channel}")
        self.inst.write(f"MEASUREMENT:MEAS{slot}:STATE ON")
        return slot
        

    def remove_measurement(self, meas_type: str, channel: int,slot: int=1, source: int = 1):
        """
        Removes the measurement of type `meas_type` on `channel`.
        """
        self.inst.write(f"MEASUREMENT:MEAS{slot}:TYPE NONE")
        self.inst.write(f"MEASUREMENT:MEAS{slot}:SOURCE{source} CH{channel}")
        self.inst.write(f"MEASUREMENT:MEAS{slot}:STATE OFF")
        self.inst.write(f"MEASUREMENT:MEAS{slot}:TYPE \"\"")  # Clear type
    
    def clear_all_measurements(self,slot: int = 1):
        for slot in range(1, 9):
            self.inst.write(f"MEASUREMENT:MEAS{slot}:STATE OFF")
            self.inst.write(f"MEASUREMENT:MEAS{slot}:TYPE NONE")
            # Optionally clear the type again for robustness
            self.inst.write(f"MEASUREMENT:MEAS{slot}:TYPE \"\"")

    def get_measurement(self,channel: int, slot:int=1,source: int = 1):
        """
        Gets the value of the measurement of type `meas_type` on `channel`.
        Args:
            meas_type (str): Measurement type (e.g., 'FREQ', 'MEAN', etc.)
            channel (int): Channel number (1-4)
            source (int): Source index (usually 1), default is 1
        Returns:
            float or str: The measurement value, or 'UNDEFINED' if not available.
        Raises:
            RuntimeError: If the measurement is not found.
        """
        self.inst.write(f"MEASUREMENT:MEAS{slot}:SOURCE{source} CH{channel}")
        value = self.inst.query(f"MEASUREMENT:MEAS{slot}:VALUE?").strip()
        return value if value else ""

    def enable_math(self, func:str):
        self.inst.write(f"MATH:DEFINE {func}")
        self.inst.write("MATH:STATE ON")

    def disable_math(self):
        self.inst.write("MATH:STATE OFF")

    # Waveform Data Transfer

    def fetch_waveform(self, channel):
        self.inst.write(f"DATA:SOU CH{channel}")
        self.inst.write("DATA:ENC RPB")
        self.inst.write("DATA:WIDTH 1")

        # Get preamble values
        x_increment = float(self.inst.query("WFMPRE:XINCR?"))
        x_origin    = float(self.inst.query("WFMPRE:XZERO?"))
        y_increment = float(self.inst.query("WFMPRE:YMULT?"))
        y_origin    = float(self.inst.query("WFMPRE:YZERO?"))
        y_reference = float(self.inst.query("WFMPRE:YOFF?"))

        # Fetch raw data
        raw_data = self.inst.query_binary_values("CURVE?", datatype='b', container=list)

        if not raw_data:
            raise ValueError("No data returned from scope.")

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
    def export_and_plot_all_waveforms(
        self,
        image=False,
        image_path="waveforms.png",
        image_format="png"
    ):
        """
        Fetch all displayed analog channels' waveforms.
        Optionally plot and/or save the plot as a simple Seaborn line plot with legends.
        Returns: dict of {channel: (times, volts)}
        Args:
            image (bool): If True, plot the waveforms.
            image_path (str): Path or filename for saving the plot.
            image_format (str): Image format (e.g., 'png', 'jpg', 'svg').
        """
        sns.set_theme(style="whitegrid")
        channel_data = {}
        timebase = None
    
        for ch in range(1, 5):
            try:
                display_state = self.inst.query(f"SELect:CH{ch}?").strip()
                if display_state.upper() == "ON" or display_state == "1":
                    times, volts = self.fetch_waveform(ch)
                    channel_data[f"CH{ch}"] = (times, volts)
                    if timebase is None:
                        timebase = times
                    print(f"Fetched CH{ch}")
                else:
                    print(f"CH{ch} is not displayed, skipping.")
            except Exception as e:
                print(f"Could not export CH{ch}: {e}")
    
        if not channel_data:
            print("No channels exported.")
            return {}
    
        if image:
            plt.figure(figsize=(10, 6))
            for ch, (times, volts) in channel_data.items():
                plt.plot(times, volts, label=ch)
            plt.xlabel("Time (s)")
            plt.ylabel("Voltage (V)")
            plt.title("Tektronix DPO4054 Waveforms")
            plt.legend()
            plt.tight_layout()
            if image_path:
                plt.savefig(image_path, format=image_format, dpi=300)
                print(f"Waveform plot saved as {image_path}")
            # plt.show()
    
        return channel_data
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

    def save_and_fetch_screen_image_usb(self, filename_on_usb="trail.png", save_to_pc="trail.png", img_format="PNG"):
        """
        Save the oscilloscope screen image to a USB stick (E:/) plugged into the scope,
        then fetch it to the PC.
        Args:
            filename_on_usb: Name for the file on the USB stick (e.g., 'trail.png').
            save_to_pc: Name for the file on the PC.
            img_format: One of 'PNG', 'BMP', 'TIFF', 'JPEG'.
        """
        img_format = img_format.upper()
        valid_formats = ['PNG', 'BMP', 'TIFF', 'JPEG']
        if img_format not in valid_formats:
            raise ValueError(f"Invalid image format. Valid options: {valid_formats}")

        scope_path = f"E:/{filename_on_usb}"

        # Step 1: Save to USB stick
        self.inst.write(f"HARDCopy:FORMat {img_format}")
        self.inst.write("HARDCopy:DEST 'FILE'")
        self.inst.write(f"HARDCopy:FILEName '{scope_path}'")
        self.inst.write("HARDCopy STARt")
        self.inst.query("*OPC?")  # Wait for operation complete

        print(f"Image saved to USB stick at {scope_path}.")

        # Step 2: Fetch from USB stick to PC
        img_data = self.inst.query_binary_values(f"MMEMory:DATA? '{scope_path}'", datatype='B', container=bytearray)
        with open(save_to_pc, 'wb') as f:
            f.write(img_data)

        print(f"File copied from scope USB to PC as {save_to_pc}")

        # Optionally, delete the file from the USB stick:
        # self.inst.write(f"FILESystem:DELete '{scope_path}'")


            # Optionally, delete the file from the scope
            # self.inst.write(f"FILESystem:DELete '{scope_path}'")


    def measure_and_save(self, channel, meas_types, filename="meas_results.json"):
        """Perform a list of measurements on a channel and save results to JSON."""
        self.clear_all_measurements()
        results = {}
        for i, mtype in enumerate(meas_types, 1):
            self.add_measurement(mtype, f"{channel}")
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
    def fetch_waveform_by_time(
        self,
        channel=1,
        t_start=None,    # Start time in seconds (relative to trigger/time origin)
        t_stop=None      # Stop time in seconds (relative to trigger/time origin)
    ):
        """
        Fetch and return time and voltage data for a specific channel and time window,
        along with timebase parameters.
        Args:
            channel (int): Channel number (1-4).
            t_start (float): Start time in seconds (None = start of record).
            t_stop (float): Stop time in seconds (None = end of record).
        Returns:
            times (list), volts (list), timebase_params (dict)
        """
        display_state = self.inst.query(f"SELect:CH{channel}?").strip()
        if not (display_state.upper() == "ON" or display_state == "1"):
            print(f"CH{channel} is not displayed, skipping.")
            return [], [], {}
    
        # Query record length and timebase params
        record_length = int(float(self.inst.query("HORizontal:RECOrdlength?")))
        x_increment = float(self.inst.query("WFMPRE:XINCR?"))
        x_origin    = float(self.inst.query("WFMPRE:XZERO?"))
        y_increment = float(self.inst.query("WFMPRE:YMULT?"))
        y_origin    = float(self.inst.query("WFMPRE:YZERO?"))
        y_reference = float(self.inst.query("WFMPRE:YOFF?"))
    
        # Calculate sample indices for the requested time window
        if t_start is None:
            start_index = 1
        else:
            start_index = int(round((t_start - x_origin) / x_increment)) + 1
            start_index = max(1, min(start_index, record_length))
        if t_stop is None:
            stop_index = record_length
        else:
            stop_index = int(round((t_stop - x_origin) / x_increment)) + 1
            stop_index = max(start_index, min(stop_index, record_length))
    
        # Set data range and format
        self.inst.write(f"DATA:START {start_index}")
        self.inst.write(f"DATA:STOP {stop_index}")
        self.inst.write(f"DATA:SOU CH{channel}")
        self.inst.write("DATA:ENC RPB")
        self.inst.write("DATA:WIDTH 1")
    
        # Fetch raw data
        raw_data = self.inst.query_binary_values("CURVE?", datatype='b', container=list)
    
        # Convert to voltages and times
        voltages = [(y - y_reference) * y_increment + y_origin for y in raw_data]
        times = [x_origin + (start_index - 1 + i) * x_increment for i in range(len(raw_data))]
    
        # Bundle timebase info
        timebase_params = {
            "x_increment": x_increment,
            "x_origin": x_origin,
            "y_increment": y_increment,
            "y_origin": y_origin,
            "y_reference": y_reference,
            "start_index": start_index,
            "stop_index": stop_index,
            "record_length": record_length
        }
    
        print(f"Fetched CH{channel}: {len(times)} samples (from t={times[0]:.6g}s to t={times[-1]:.6g}s)")
        return times, voltages, timebase_params
    def fetch_channel_waveform(self, channel=1, num_samples=None):
        """
        Fetch and return time and voltage data for a specific channel and number of samples.
        Args:
            channel (int): Channel number (1-4).
            num_samples (int, optional): Number of samples to fetch from the start.
        Returns:
            times (list), volts (list), timebase_params (dict)
        """
        # Check if channel is ON
        display_state = self.inst.query(f"SELect:CH{channel}?").strip()
        if not (display_state.upper() == "ON" or display_state == "1"):
            print(f"CH{channel} is not displayed, skipping.")
            return [], [], {}

        # Query the current record length (number of points available)
        record_length = int(float(self.inst.query("HORizontal:RECOrdlength?")))

        # Determine start and stop indices
        if num_samples is not None:
            start = 1
            stop = min(num_samples, record_length)
        else:
            start = 1
            stop = record_length

        # Set data range
        self.inst.write(f"DATA:START {start}")
        self.inst.write(f"DATA:STOP {stop}")

        # Set data source and format
        self.inst.write(f"DATA:SOU CH{channel}")
        self.inst.write("DATA:ENC RPB")   # Signed 8-bit binary
        self.inst.write("DATA:WIDTH 1")   # 1 byte per sample

        # Get waveform preamble (timebase info)
        x_increment = float(self.inst.query("WFMPRE:XINCR?"))
        x_origin    = float(self.inst.query("WFMPRE:XZERO?"))
        y_increment = float(self.inst.query("WFMPRE:YMULT?"))
        y_origin    = float(self.inst.query("WFMPRE:YZERO?"))
        y_reference = float(self.inst.query("WFMPRE:YOFF?"))

        # Fetch raw data
        raw_data = self.inst.query_binary_values("CURVE?", datatype='b', container=list)

        # Convert to voltages and times
        volts = [(y - y_reference) * y_increment + y_origin for y in raw_data]
        times = [x_origin + (start - 1 + i) * x_increment for i in range(len(raw_data))]

        timebase_params = {
            "x_increment": x_increment,
            "x_origin": x_origin,
            "y_increment": y_increment,
            "y_origin": y_origin,
            "y_reference": y_reference,
            "start_index": start,
            "stop_index": stop,
            "record_length": record_length
        }

        print(f"Fetched CH{channel}: {len(times)} samples (from {times[0]:.6g}s to {times[-1]:.6g}s)")
        return times, volts, timebase_params

    def close(self):
        self.inst.close()
        self.rm.close()

    def set_scope_timebase_and_fetch(self, fs=None, num_samples=None, channel=1):
        """
        Set the oscilloscope's timebase and record length for the desired sampling frequency and number of samples,
        if specified. Fetch waveform data using the actual dt from the scope.
        Returns: times, volts, timebase_params
        """
        # Query current settings if needed
        if num_samples is None:
            num_samples = int(float(self.inst.query("HORizontal:RECOrdlength?")))
        if fs is None:
            dt = float(self.inst.query("WFMPRE:XINCR?"))
            fs = 1.0 / dt

        # Set scope only if user provided both fs and num_samples
        if fs is not None and num_samples is not None:
            time_per_div = num_samples / (fs * 10)
            self.inst.write(f"HORizontal:MAIn:SCAle {time_per_div}")
            self.inst.write(f"HORizontal:RECOrdlength {num_samples}")
            time.sleep(0.5)  # Let scope settle

        # Fetch waveform
        times, volts, timebase = self.fetch_channel_waveform(channel=channel, num_samples=num_samples)
        dt = timebase["x_increment"]
        actual_fs = 1.0 / dt
        print(f"Requested fs: {fs}, Actual scope fs: {actual_fs:.2f} Hz, dt: {dt:.2e} s, N: {len(volts)}")
        return times, volts, timebase

    def analyze_fft_with_inputs(self, num_samples=None, fs=None, window_type='hann', channel=1):
        """
        Set scope, fetch data, and perform FFT/signal analysis for a given channel.
        If num_samples or fs is not provided, uses instrument's current settings.
        Returns:
            metrics (dict): Dictionary of all computed signal metrics.
        """
        times, volts, timebase = self.set_scope_timebase_and_fetch(fs, num_samples, channel)
        N = len(volts)
        if N == 0:
            raise ValueError("No data fetched from oscilloscope.")
        dt = timebase["x_increment"]
        fs_actual = 1.0 / dt

        # Apply window
        window = getattr(windows, window_type)(N)
        volts_win = volts * window

        # FFT
        fft_vals = np.fft.fft(volts_win)
        fft_freqs = np.fft.fftfreq(N, dt)
        pos_mask = fft_freqs > 0
        fft_freqs_pos = fft_freqs[pos_mask]
        fft_vals_pos = np.abs(fft_vals[pos_mask])

        # Find peaks (harmonics)
        peaks, _ = find_peaks(fft_vals_pos, height=np.max(fft_vals_pos)*0.05)
        if len(peaks) == 0:
            nanarr = np.full(10, np.nan)
            return {
                "Fc": np.nan,
                "Fundamental Amplitude": np.nan,
                "Harmonics Frequencies": nanarr,
                "Harmonics Amplitudes": nanarr,
                "SNR_dB": np.nan,
                "THD_dB": np.nan,
                "DNR_dB": np.nan,
                "Signal RMS": np.nan,
                "Total RMS": np.nan,
                "Noise RMS": np.nan,
                "fft_freqs": fft_freqs_pos,
                "fft_magnitude": fft_vals_pos,
                "window_type": window_type,
                "N_samples": N,
                "dt": dt,
                "fs": fs_actual,
                "channel": channel,
                "timebase": timebase,
            }

        sorted_peaks = peaks[np.argsort(fft_vals_pos[peaks])[::-1]]
        fundamental_idx = sorted_peaks[0]
        Fc = fft_freqs_pos[fundamental_idx]
        fundamental_amp = fft_vals_pos[fundamental_idx]

        harmonics_freqs = Fc * np.arange(1, 11)
        harmonics_amps = []
        for h_freq in harmonics_freqs:
            idx = np.argmin(np.abs(fft_freqs_pos - h_freq))
            harmonics_amps.append(fft_vals_pos[idx])

        signal_rms = harmonics_amps[0] / np.sqrt(2)
        total_rms = np.sqrt(np.mean(volts_win**2))
        harmonics_bins = [np.argmin(np.abs(fft_freqs_pos - h)) for h in harmonics_freqs]
        noise_bins = np.ones_like(fft_vals_pos, dtype=bool)
        for b in harmonics_bins:
            noise_bins[max(0, b-1):b+2] = False
        noise_rms = np.sqrt(np.mean(fft_vals_pos[noise_bins]**2))
        SNR = 20 * np.log10(signal_rms / noise_rms) if noise_rms > 0 else np.nan
        thd_numerator = np.sqrt(np.sum(np.array(harmonics_amps[1:])**2))
        THD = 20 * np.log10(thd_numerator / harmonics_amps[0]) if harmonics_amps[0] > 0 else np.nan
        try:
            DNR = 20 * np.log10(np.max(fft_vals_pos) / np.min(fft_vals_pos[fft_vals_pos > 0]))
        except:
            DNR = np.nan

        metrics = {
            "Fc": Fc,
            "Fundamental Amplitude": fundamental_amp,
            "Harmonics Frequencies": harmonics_freqs,
            "Harmonics Amplitudes": harmonics_amps,
            "SNR_dB": SNR,
            "THD_dB": THD,
            "DNR_dB": DNR,
            "Signal RMS": signal_rms,
            "Total RMS": total_rms,
            "Noise RMS": noise_rms,
            "fft_freqs": fft_freqs_pos,
            "fft_magnitude": fft_vals_pos,
            "window_type": window_type,
            "N_samples": N,
            "dt": dt,
            "fs": fs_actual,
            "channel": channel,
            "timebase": timebase,
        }
        return metrics
