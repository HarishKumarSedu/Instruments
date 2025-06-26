import pyvisa

def _format_chanlist(chan):
    """Format channel for SCPI commands."""
    if isinstance(chan, int):
        return f"(@{chan})"
    if isinstance(chan, str):
        if chan.startswith("(@") and chan.endswith(")"):
            return chan
        return f"(@{chan})"
    raise ValueError("Channel must be int or string.")

import pyvisa as visa
class N67xx:
    def __init__(self, inst_id:str=''):
        self.inst = visa.ResourceManager().open_resource(inst_id)

    # --- 1. ABORt Commands ---
    def abort_acquire(self, chan=1):
        self.inst.write(f"ABORt:ACQuire {_format_chanlist(chan)}")
    def abort_elog(self, chan=1):
        self.inst.write(f"ABORt:ELOG {_format_chanlist(chan)}")
    def abort_transient(self, chan=1):
        self.inst.write(f"ABORt:TRANsient {_format_chanlist(chan)}")
    def configure_abort(self, chan=1):
        self.abort_acquire(chan)
        self.abort_elog(chan)
        self.abort_transient(chan)

    # --- 2. CALibrate Commands ---
    def calibrate_current_level(self, value, chan=1):
        self.inst.write(f"CALibrate:CURRent:LEVel {value}, {_format_chanlist(chan)}")
    def calibrate_current_limit_negative(self, value, chan=1):
        self.inst.write(f"CALibrate:CURRent:LIMit:NEGative {value}, {_format_chanlist(chan)}")
    def calibrate_current_limit_positive(self, value, chan=1):
        self.inst.write(f"CALibrate:CURRent:LIMit:POSitive {value}, {_format_chanlist(chan)}")
    def calibrate_current_measure(self, value, chan=1):
        self.inst.write(f"CALibrate:CURRent:MEASure {value}, {_format_chanlist(chan)}")
    def calibrate_current_peak(self, chan=1):
        self.inst.write(f"CALibrate:CURRent:PEAK {_format_chanlist(chan)}")
    def calibrate_data(self, value):
        self.inst.write(f"CALibrate:DATA {value}")
    def calibrate_date(self, date, chan=1):
        self.inst.write(f'CALibrate:DATE "{date}", {_format_chanlist(chan)}')
    def calibrate_downprogrammer(self, chan=1):
        self.inst.write(f"CALibrate:CURRent:DPRog {_format_chanlist(chan)}")
    def calibrate_level_step(self, step):
        self.inst.write(f"CALibrate:CURRent:LEVel {step}")
    def calibrate_password(self, value):
        self.inst.write(f"CALibrate:PASSword {value}")
    def calibrate_resistance(self, value, chan=1):
        self.inst.write(f"CALibrate:RESistance {value}, {_format_chanlist(chan)}")
    def calibrate_save(self):
        self.inst.write("CALibrate:SAVE")
    def calibrate_state(self, state=True, value=""):
        val = "ON" if state else "OFF"
        self.inst.write(f"CALibrate:STATE {val} {value}")
    def calibrate_voltage_level(self, value, chan=1):
        self.inst.write(f"CALibrate:VOLTage:LEVel {value}, {_format_chanlist(chan)}")
    def calibrate_voltage_cmrr(self, chan=1):
        self.inst.write(f"CALibrate:VOLTage:CMRR {_format_chanlist(chan)}")
    def calibrate_voltage_limit_positive(self, value, chan=1):
        self.inst.write(f"CALibrate:VOLTage:LIMit:POSitive {value}, {_format_chanlist(chan)}")
    def calibrate_voltage_measure(self, value, chan=1):
        self.inst.write(f"CALibrate:VOLTage:MEASure {value}, {_format_chanlist(chan)}")
    def calibrate_voltage_aux(self, chan=1):
        self.inst.write(f"CALibrate:VOLTage:AUXiliary {_format_chanlist(chan)}")
    def configure_calibrate(self, chan=1, current_level=1.0, voltage_level=1.0):
        self.calibrate_current_level(current_level, chan)
        self.calibrate_voltage_level(voltage_level, chan)
        self.calibrate_save()

    # --- 3. Common Commands ---
    def clear_status(self):
        self.inst.write("*CLS")
    def bus_trigger(self):
        self.inst.write("*TRG")
    def set_event_status_enable(self, value):
        self.inst.write(f"*ESE {value}")
    def get_event_status_enable(self):
        return self.inst.query("*ESE?").strip()
    def get_event_status_register(self):
        return self.inst.query("*ESR?").strip()
    def get_identification(self):
        return self.inst.query("*IDN?").strip()
    def set_operation_complete(self):
        self.inst.write("*OPC")
    def get_operation_complete(self):
        return self.inst.query("*OPC?").strip()
    def reset(self):
        self.inst.write("*RST")
    def get_service_request_enable(self):
        return self.inst.query("*SRE?").strip()
    def set_service_request_enable(self, value):
        self.inst.write(f"*SRE {value}")
    def get_status_byte(self):
        return self.inst.query("*STB?").strip()
    def get_test(self):
        return self.inst.query("*TST?").strip()
    def configure_common(self):
        self.clear_status()
        self.reset()

    # --- 4. DISPlay Commands ---
    def display_window_channel(self, chan=1):
        self.inst.write(f"DISPlay:WINDow:CHANnel {chan}")
    def display_window_view(self, view="METER1"):
        self.inst.write(f"DISPlay:WINDow:VIEW {view}")
    def configure_display(self, chan=1, view="METER1"):
        self.display_window_channel(chan)
        self.display_window_view(view)

    # --- 5. FETCh Commands ---
    def fetch_current_dc(self, chan=1):
        return self.inst.query(f"FETCh:CURRent:DC? {_format_chanlist(chan)}").strip()
    def fetch_current_acdc(self, chan=1):
        return self.inst.query(f"FETCh:CURRent:ACDC? {_format_chanlist(chan)}").strip()
    def fetch_current_high(self, chan=1):
        return self.inst.query(f"FETCh:CURRent:HIGH? {_format_chanlist(chan)}").strip()
    def fetch_current_low(self, chan=1):
        return self.inst.query(f"FETCh:CURRent:LOW? {_format_chanlist(chan)}").strip()
    def fetch_current_max(self, chan=1):
        return self.inst.query(f"FETCh:CURRent:MAXimum? {_format_chanlist(chan)}").strip()
    def fetch_current_min(self, chan=1):
        return self.inst.query(f"FETCh:CURRent:MINimum? {_format_chanlist(chan)}").strip()
    def fetch_power_dc(self, chan=1):
        return self.inst.query(f"FETCh:POWer:DC? {_format_chanlist(chan)}").strip()
    def fetch_voltage_dc(self, chan=1):
        return self.inst.query(f"FETCh:VOLTage:DC? {_format_chanlist(chan)}").strip()
    def fetch_voltage_acdc(self, chan=1):
        return self.inst.query(f"FETCh:VOLTage:ACDC? {_format_chanlist(chan)}").strip()
    def fetch_voltage_high(self, chan=1):
        return self.inst.query(f"FETCh:VOLTage:HIGH? {_format_chanlist(chan)}").strip()
    def fetch_voltage_low(self, chan=1):
        return self.inst.query(f"FETCh:VOLTage:LOW? {_format_chanlist(chan)}").strip()
    def fetch_voltage_max(self, chan=1):
        return self.inst.query(f"FETCh:VOLTage:MAXimum? {_format_chanlist(chan)}").strip()
    def fetch_voltage_min(self, chan=1):
        return self.inst.query(f"FETCh:VOLTage:MINimum? {_format_chanlist(chan)}").strip()
    def configure_fetch(self, chan=1):
        return {
            "current_dc": self.fetch_current_dc(chan),
            "voltage_dc": self.fetch_voltage_dc(chan),
            "power_dc": self.fetch_power_dc(chan)
        }
        
    def measure_current_dc(self, chan=1):
        return self.inst.query(f"MEASure:CURRent:DC? {_format_chanlist(chan)}").strip()

    def measure_current_acdc(self, chan=1):
        return self.inst.query(f"MEASure:CURRent:ACDC? {_format_chanlist(chan)}").strip()

    def measure_current_high(self, chan=1):
        return self.inst.query(f"MEASure:CURRent:HIGH? {_format_chanlist(chan)}").strip()

    def measure_current_low(self, chan=1):
        return self.inst.query(f"MEASure:CURRent:LOW? {_format_chanlist(chan)}").strip()

    def measure_current_max(self, chan=1):
        return self.inst.query(f"MEASure:CURRent:MAXimum? {_format_chanlist(chan)}").strip()

    def measure_current_min(self, chan=1):
        return self.inst.query(f"MEASure:CURRent:MINimum? {_format_chanlist(chan)}").strip()

    def measure_power_dc(self, chan=1):
        return self.inst.query(f"MEASure:POWer:DC? {_format_chanlist(chan)}").strip()

    def measure_voltage_dc(self, chan=1):
        return self.inst.query(f"MEASure:VOLTage:DC? {_format_chanlist(chan)}").strip()

    def measure_voltage_acdc(self, chan=1):
        return self.inst.query(f"MEASure:VOLTage:ACDC? {_format_chanlist(chan)}").strip()

    def measure_voltage_high(self, chan=1):
        return self.inst.query(f"MEASure:VOLTage:HIGH? {_format_chanlist(chan)}").strip()

    def measure_voltage_low(self, chan=1):
        return self.inst.query(f"MEASure:VOLTage:LOW? {_format_chanlist(chan)}").strip()

    def measure_voltage_max(self, chan=1):
        return self.inst.query(f"MEASure:VOLTage:MAXimum? {_format_chanlist(chan)}").strip()

    def measure_voltage_min(self, chan=1):
        return self.inst.query(f"MEASure:VOLTage:MINimum? {_format_chanlist(chan)}").strip()

    def configure_measure(self, chan=1):
        return {
            "current_dc": self.measure_current_dc(chan),
            "voltage_dc": self.measure_voltage_dc(chan),
            "power_dc": self.measure_power_dc(chan)
        }
    # --- 6. FORMAt Commands ---
    def set_format_data(self, fmt="ASCII"):
        self.inst.write(f"FORMat:DATA {fmt}")
    def set_format_border(self, border="NORMal"):
        self.inst.write(f"FORMat:BORDer {border}")
    def configure_format(self, fmt="ASCII", border="NORMal"):
        self.set_format_data(fmt)
        self.set_format_border(border)

    # --- 7. INITiate Commands ---
    def initiate_acquire(self, chan=1):
        self.inst.write(f"INITiate:ACQuire {_format_chanlist(chan)}")
    def initiate_elog(self, chan=1):
        self.inst.write(f"INITiate:ELOG {_format_chanlist(chan)}")
    def initiate_transient(self, chan=1):
        self.inst.write(f"INITiate:TRANsient {_format_chanlist(chan)}")
    def configure_initiate(self, chan=1):
        self.initiate_acquire(chan)
        self.initiate_elog(chan)
        self.initiate_transient(chan)
    

    # --- 8. arb commands  ---
    def arb_voltage_sine_generate(self, channel=1, amplitude=1,frequency=100,
                                  repeat_continuous=False, repeat_count: int = 100,
                                  trigger_source='BUS', output_on=True):
        """
        Configure the Keysight N6705 to generate a sinusoidal arbitrary voltage waveform.

        Parameters:
        - channel: Power supply channel number (default 1)
        - amplitude: Peak amplitude of sine wave in volts (default 1.0 V)
        - offset: DC offset voltage (default 0.0 V)
        - frequency: Frequency of sine wave in Hz (default 1000 Hz)
        - repeat_continuous: Boolean, True for infinite repeats, False for finite repeats
        - repeat_count: Number of repeats if repeat_continuous is False (default 1)
        - trigger_source: Trigger source for ARB ('BUS', 'EXT', 'IMM', etc.) (default 'IMM')
        - output_on: Boolean to enable output after configuration (default True)
        """

        ch_str = f"(@{channel})"
        self.inst.write(f"*RST")
        self.clear_status()
        # Set voltage mode to ARB on specified channel (important to avoid FIXed mode error)
        self.inst.write(f"VOLT:MODE ARB,{ch_str}")
        self.inst.write(f"ARB:FUNC:TYPE VOLT,{ch_str}")
        self.inst.write(f"ARB:FUNC:SHAP SIN,{ch_str}")

        # Configure sine waveform parameters
        self.inst.write(f"ARB:VOLT:SIN:AMPL {amplitude},{ch_str}")
        self.inst.write(f"ARB:VOLT:SIN:OFFS {amplitude},{ch_str}")
        self.inst.write(f"ARB:VOLT:SIN:FREQ {frequency},{ch_str}")

        # Set ARB repeat count: 'INF' for continuous, or specific count
        repeat_val = 'INF' if repeat_continuous else str(repeat_count)
        self.inst.write(f"ARB:COUN {repeat_val},{ch_str}")

        # Set ARB termination behavior: remain at last ARB value after completion
        self.inst.write(f"ARB:TERM:LAST ON,{ch_str}")

        # Set ARB trigger source (BUS, EXT, IMM, etc.)
        self.inst.write(f"TRIG:ARB:SOUR BUS")

        # Enable or disable output
        self.inst.write(f"OUTP {'ON' if output_on else 'OFF'},{ch_str}")

        # Initiate transient ARB sequence on the channel
        self.inst.write(f"INIT:TRAN {ch_str}")

        # If trigger source is immediate, send *TRG to start waveform immediately
        # if trigger_source.upper() == 'IMM':
        self.inst.write("*TRG")

        # print(f"Sinusoidal ARB waveform started on channel {channel} with amplitude {amplitude} V, "
        #       f"offset {amplitude} V, frequency {frequency} Hz, repeat_continuous={repeat_continuous}, "
        #       f"repeat_count={repeat_count}, trigger source '{trigger_source}', output_on={output_on}.")

        # # Optional: Check for errors after configuration
        # print("System Error After Config:", self.system_error())

    # --- 8. OUTPut Commands ---
    def output_state(self, channel=1,state=True ):
        val = "ON" if state else "OFF"
        self.inst.write(f"OUTPut:STATe {val}, {_format_chanlist(channel)}")
    def output_couple_state(self, state=True):
        val = "ON" if state else "OFF"
        self.inst.write(f"OUTPut:COUPle:STATe {val}")
    def output_channel(self, channels=(1,)):
        ch_str = ",".join(str(c) for c in channels)
        self.inst.write(f"OUTPut:CHANNel {ch_str}")
    def output_delay_fall(self, value=0.01, chan=1):
        self.inst.write(f"OUTPut:DELay:FALL {value}, {_format_chanlist(chan)}")
    def output_delay_rise(self, value=0.01, chan=1):
        self.inst.write(f"OUTPut:DELay:RISE {value}, {_format_chanlist(chan)}")
    def output_inhibit_mode(self, mode="LATCHing"):
        self.inst.write(f"OUTPut:INHibit:MODE {mode.upper()}")
    def output_pon_state(self, state="RST"):
        self.inst.write(f"OUTPut:PON:STATe {state.upper()}")
    def output_protection_clear(self, chan=1):
        self.inst.write(f"OUTPut:PROTection:CLEar {_format_chanlist(chan)}")
    def output_protection_couple(self, state=True):
        val = "ON" if state else "OFF"
        self.inst.write(f"OUTPut:PROTection:COUPle {val}")
    def output_protection_delay(self, value=0.01, chan=1):
        self.inst.write(f"OUTPut:PROTection:DELay {value}, {_format_chanlist(chan)}")
    def output_oscillation(self, state=True, chan=1):
        val = "ON" if state else "OFF"
        self.inst.write(f"OUTPut:PROTection:OSCillation {val}, {_format_chanlist(chan)}")
    def output_watchdog_state(self, state=True):
        val = "ON" if state else "OFF"
        self.inst.write(f"OUTPut:WDOG:STATe {val}")
    def output_watchdog_delay(self, value=1.0):
        self.inst.write(f"OUTPut:WDOG:DELay {value}")
    def output_relay_polarity(self, polarity="NORMal", chan=1):
        self.inst.write(f"OUTPut:RELay:POLarity {polarity.upper()}, {_format_chanlist(chan)}")
    def configure_output(self, chan=1):
        self.output_state(True, chan)
        self.output_couple_state(True)
        self.output_delay_fall(0.01, chan)
        self.output_delay_rise(0.01, chan)
        self.output_protection_clear(chan)
        self.output_protection_couple(True)
        self.output_oscillation(True, chan)
        self.output_watchdog_state(True)
        self.output_watchdog_delay(1.0)
        self.output_relay_polarity("NORMal", chan)

 # --- SENSe Block ---
    def sense_current_ccompensate(self, state=True, chan=1):
        val = "ON" if state else "OFF"
        self.inst.write(f"SENSe:CURRent:CCOMpensate {val}, {_format_chanlist(chan)}")

    def sense_current_range(self, value=1.0, chan=1):
        self.inst.write(f"SENSe:CURRent:DC:RANGe {value}, {_format_chanlist(chan)}")

    def sense_current_range_upper(self, value=1.0, chan=1):
        self.inst.write(f"SENSe:CURRent:DC:RANGe:UPPer {value}, {_format_chanlist(chan)}")

    def sense_current_autorange(self, state=True, chan=1):
        val = "ON" if state else "OFF"
        self.inst.write(f"SENSe:CURRent:DC:AUTO {val}, {_format_chanlist(chan)}")

    def sense_voltage_range(self, value=10.0, chan=1):
        self.inst.write(f"SENSe:VOLTage:DC:RANGe {value}, {_format_chanlist(chan)}")

    def sense_voltage_range_upper(self, value=10.0, chan=1):
        self.inst.write(f"SENSe:VOLTage:DC:RANGe:UPPer {value}, {_format_chanlist(chan)}")

    def sense_voltage_autorange(self, state=True, chan=1):
        val = "ON" if state else "OFF"
        self.inst.write(f"SENSe:VOLTage:DC:AUTO {val}, {_format_chanlist(chan)}")

    def sense_function(self, function="VOLTage", chan=1):
        self.inst.write(f'SENSe:FUNCtion "{function.upper()}", {_format_chanlist(chan)}')

    def sense_current_enable(self, state=True, chan=1):
        val = "ON" if state else "OFF"
        self.inst.write(f"SENSe:CURRent {val}, {_format_chanlist(chan)}")

    def sense_voltage_enable(self, state=True, chan=1):
        val = "ON" if state else "OFF"
        self.inst.write(f"SENSe:VOLTage {val}, {_format_chanlist(chan)}")

    def sense_voltage_input(self, source="MAIN", chan=1):
        self.inst.write(f"SENSe:VOLTage:INPut {source.upper()}, {_format_chanlist(chan)}")

    def sense_sweep_offset_points(self, points=0, chan=1):
        self.inst.write(f"SENSe:SWEep:OFFSet:POINts {points}, {_format_chanlist(chan)}")

    def sense_sweep_points(self, points=1, chan=1):
        self.inst.write(f"SENSe:SWEep:POINts {points}, {_format_chanlist(chan)}")

    def sense_sweep_interval(self, interval=0.01, chan=1):
        self.inst.write(f"SENSe:SWEep:TINTerval {interval}, {_format_chanlist(chan)}")

    def sense_resolution(self, resolution="RES20", chan=1):
        self.inst.write(f"SENSe:RESolution {resolution.upper()}, {_format_chanlist(chan)}")

    def sense_window_type(self, wtype="HANNing", chan=1):
        self.inst.write(f"SENSe:WINDow:TYPE {wtype.upper()}, {_format_chanlist(chan)}")

    def configure_sense(self, chan=1):
        self.sense_current_ccompensate(True, chan)
        self.sense_current_range(1.0, chan)
        self.sense_current_autorange(True, chan)
        self.sense_voltage_range(10.0, chan)
        self.sense_voltage_autorange(True, chan)
        self.sense_function("VOLTage", chan)
        self.sense_current_enable(True, chan)
        self.sense_voltage_enable(True, chan)
        self.sense_resolution("RES20", chan)
        self.sense_window_type("HANNing", chan)

    # --- SOURce Block ---
    def source_current_immediate(self, value=1.0, chan=1):
        self.inst.write(f"SOURce:CURRent:LEVel:IMMediate:AMPLitude {value}, {_format_chanlist(chan)}")

    def source_current_triggered(self, value=1.0, chan=1):
        self.inst.write(f"SOURce:CURRent:LEVel:TRIGgered:AMPLitude {value}, {_format_chanlist(chan)}")

    def source_current_limit_positive(self, value=1.0, chan=1):
        self.inst.write(f"SOURce:CURRent:LIMit:POSitive:IMMediate:AMPLitude {value}, {_format_chanlist(chan)}")

    def source_current_limit_negative(self, value=0.0, chan=1):
        self.inst.write(f"SOURce:CURRent:LIMit:NEGative:IMMediate:AMPLitude {value}, {_format_chanlist(chan)}")

    def source_current_mode(self, mode="FIXed", chan=1):
        self.inst.write(f"SOURce:CURRent:MODE {mode.upper()}, {_format_chanlist(chan)}")

    def source_current_protection_delay(self, delay=0.01, chan=1):
        self.inst.write(f"SOURce:CURRent:PROTection:DELay:TIME {delay}, {_format_chanlist(chan)}")

    def source_current_protection_state(self, state=True, chan=1):
        val = "ON" if state else "OFF"
        self.inst.write(f"SOURce:CURRent:PROTection:STATe {val}, {_format_chanlist(chan)}")

    def source_current_range(self, value=1.0, chan=1):
        self.inst.write(f"SOURce:CURRent:RANGe {value}, {_format_chanlist(chan)}")

    def source_current_slew(self, value=1.0, chan=1):
        self.inst.write(f"SOURce:CURRent:SLEW:IMMediate {value}, {_format_chanlist(chan)}")

    def source_voltage_immediate(self, value=5.0, chan=1):
        self.inst.write(f"SOURce:VOLTage:LEVel:IMMediate:AMPLitude {value}, {_format_chanlist(chan)}")

    def source_voltage_triggered(self, value=5.0, chan=1):
        self.inst.write(f"SOURce:VOLTage:LEVel:TRIGgered:AMPLitude {value}, {_format_chanlist(chan)}")

    def source_voltage_bandwidth(self, bw="LOW", chan=1):
        self.inst.write(f"SOURce:VOLTage:BWIDth {bw.upper()}, {_format_chanlist(chan)}")

    def source_voltage_limit_positive(self, value=5.0, chan=1):
        self.inst.write(f"SOURce:VOLTage:LIMit:POSitive:IMMediate:AMPLitude {value}, {_format_chanlist(chan)}")

    def source_voltage_limit_negative(self, value=0.0, chan=1):
        self.inst.write(f"SOURce:VOLTage:LIMit:NEGative:IMMediate:AMPLitude {value}, {_format_chanlist(chan)}")

    def source_voltage_mode(self, mode="FIXed", chan=1):
        self.inst.write(f"SOURce:VOLTage:MODE {mode.upper()}, {_format_chanlist(chan)}")

    def source_voltage_protection_level(self, value=6.0, chan=1):
        self.inst.write(f"SOURce:VOLTage:PROTection:LEVel {value}, {_format_chanlist(chan)}")

    def source_voltage_protection_delay(self, delay=0.01, chan=1):
        self.inst.write(f"SOURce:VOLTage:PROTection:DELay:TIME {delay}, {_format_chanlist(chan)}")

    def source_voltage_range(self, value=10.0, chan=1):
        self.inst.write(f"SOURce:VOLTage:RANGe {value}, {_format_chanlist(chan)}")

    def source_voltage_slew(self, value=1.0, chan=1):
        self.inst.write(f"SOURce:VOLTage:SLEW:IMMediate {value}, {_format_chanlist(chan)}")
    def set_voltage(self,channel:int,voltage: float=0.0):
        self.inst.write(f'VOLT {str(voltage)},(@{str(channel)})')
    def set_current(self,channel:int,current: float=0.0):
        self.inst.write(f'CURR {str(current)},(@{str(channel)})')
    def get_emoulation_mode(self,channel:int):
        return self.inst.query(f'EMUL? (@{str(channel)})').strip()
    def get_priority(self,channel:int):
        return self.inst.query(f'FUNC? (@{str(channel)})').strip()
    def get_outp_state(self,channel:int):
        state = self.inst.query(f'OUTP:STATE? (@{str(channel)})').strip()
        return True if state == 'ON' else False
    def configure_voltage_source(self, channel,voltage_setpoint=0, voltage_limit=20, current_limit=3,
                                  current_protection_on=True,
                                 four_wire=False, output_HiZ=True,
                                 voltage_slew=3300):
        """
        Configure the voltage source on the specified channel.
        Parameters:
        - channel: int or str, output channel number (e.g., 3)
        - voltage_limit: float, voltage limit in volts
        - current_limit: float, current limit in amps
        - voltage_setpoint: float, output voltage setpoint in volts (default 0)
        - current_protection_on: bool, enable or disable current protection
        - four_wire: bool, True for 4-wire (internal) sensing, False for 2-wire (external)
        - output_HiZ: bool, True for HIGHZ output mode, False for LOWZ
        - voltage_slew: float, slew rate in V/s
        """
        ch_str = f"(@{channel})"  # Wrap channel as string in SCPI format
        # Map booleans to SCPI strings
        voltage_sense_str = 'EXTernal' if four_wire else 'INTernal'
        output_mode_str = 'HIGHZ' if output_HiZ else 'LOWZ'
        # Set emulation mode (example: PS1Q)
        self.inst.write(f'EMULation PS1Q,{ch_str}')
        # Set function priority to voltage
        self.inst.write(f'FUNC VOLT,{ch_str}')
        # Set voltage limit
        # self.inst.write(f'VOLT:LIM {voltage_limit},{ch_str}')
        # Set current limit
        self.inst.write(f'CURR:LIM {current_limit},{ch_str}')
        # Set output voltage (default 0)
        self.inst.write(f'VOLT {voltage_setpoint},{ch_str}')
        # Enable or disable current protection
        state = 'ON' if current_protection_on else 'OFF'
        self.inst.write(f'CURRent:PROTection:STATe {state},{ch_str}')
        # Set voltage sense source based on four_wire boolean
        self.inst.write(f'VOLTage:SENSe:SOURce {voltage_sense_str},{ch_str}')
        # Set output terminal mode based on output_HiZ boolean
        self.inst.write(f'OUTPut:TMODe {output_mode_str},{ch_str}')
        # Set voltage slew rate
        self.inst.write(f'VOLT:SLEW {voltage_slew},{ch_str}')
        
    def configure_current_sink_source(self, channel,current_setpoint=0, voltage_limit=6,four_wire=False):
        """
        Configure the voltage source on the specified channel.
        Parameters:
        - channel: int or str, output channel number (e.g., 3)
        - voltage_limit: float, voltage limit in volts
        - current_limit: float, current limit in amps
        - voltage_setpoint: float, output voltage setpoint in volts (default 0)
        - current_protection_on: bool, enable or disable current protection
        - four_wire: bool, True for 4-wire (internal) sensing, False for 2-wire (external)
        - output_HiZ: bool, True for HIGHZ output mode, False for LOWZ
        - voltage_slew: float, slew rate in V/s
        """
        ch_str = f"(@{channel})"  # Wrap channel as string in SCPI format
        # Map booleans to SCPI strings
        voltage_sense_str = 'EXTernal' if four_wire else 'INTernal'
        # Set emulation mode (example: PS1Q)
        self.inst.write(f'EMULation PS2Q,{ch_str}')
        # Set function priority to voltage
        self.inst.write(f'FUNC CURR,{ch_str}')
        # Set voltage limit
        self.inst.write(f'VOLT:LIM {voltage_limit},{ch_str}')
        # Set current limit
        # self.inst.write(f'CURR:LIM {current_limit},{ch_str}')
        # Set output current (default 0)
        self.inst.write(f'CURR {current_setpoint},{ch_str}')
        # Set voltage sense source based on four_wire boolean
        self.inst.write(f'VOLTage:SENSe:SOURce {voltage_sense_str},{ch_str}')

    def configure_volt_meter(self,channel:int):
        self.inst.write(f'EMULation VMETER,(@{str(channel)})')
    def configure_CC_load(self,channel:int):
        self.inst.write(f'EMULation CCLOAD,(@{str(channel)})')
    def configure_current_meter(self,channel:int):
        self.inst.write(f'EMULation AMETER,(@{str(channel)})')

    # --- OUTPut Block ---
    def output_state(self, state=True, chan=1):
        val = "ON" if state else "OFF"
        self.inst.write(f"OUTPut:STATe {val}, {_format_chanlist(chan)}")

    def output_couple_state(self, state=True):
        val = "ON" if state else "OFF"
        self.inst.write(f"OUTPut:COUPle:STATe {val}")

    def output_channel(self, channels=(1,)):
        ch_str = ",".join(str(c) for c in channels)
        self.inst.write(f"OUTPut:CHANNel {ch_str}")

    def output_delay_fall(self, value=0.01, chan=1):
        self.inst.write(f"OUTPut:DELay:FALL {value}, {_format_chanlist(chan)}")

    def output_delay_rise(self, value=0.01, chan=1):
        self.inst.write(f"OUTPut:DELay:RISE {value}, {_format_chanlist(chan)}")

    def output_inhibit_mode(self, mode="LATCHing"):
        self.inst.write(f"OUTPut:INHibit:MODE {mode.upper()}")

    def output_pon_state(self, state="RST"):
        self.inst.write(f"OUTPut:PON:STATe {state.upper()}")

    def output_protection_clear(self, chan=1):
        self.inst.write(f"OUTPut:PROTection:CLEar {_format_chanlist(chan)}")

    def output_protection_couple(self, state=True):
        val = "ON" if state else "OFF"
        self.inst.write(f"OUTPut:PROTection:COUPle {val}")

    def output_protection_delay(self, value=0.01, chan=1):
        self.inst.write(f"OUTPut:PROTection:DELay {value}, {_format_chanlist(chan)}")

    def output_oscillation(self, state=True, chan=1):
        val = "ON" if state else "OFF"
        self.inst.write(f"OUTPut:PROTection:OSCillation {val}, {_format_chanlist(chan)}")

    def output_watchdog_state(self, state=True):
        val = "ON" if state else "OFF"
        self.inst.write(f"OUTPut:WDOG:STATe {val}")

    def output_watchdog_delay(self, value=1.0):
        self.inst.write(f"OUTPut:WDOG:DELay {value}")

    def output_relay_polarity(self, polarity="NORMal", chan=1):
        self.inst.write(f"OUTPut:RELay:POLarity {polarity.upper()}, {_format_chanlist(chan)}")

    def configure_output(self, chan=1):
        self.output_state(True, chan)
        self.output_couple_state(True)
        self.output_delay_fall(0.01, chan)
        self.output_delay_rise(0.01, chan)
        self.output_protection_clear(chan)
        self.output_protection_couple(True)
        self.output_oscillation(True, chan)
        self.output_watchdog_state(True)
        self.output_watchdog_delay(1.0)
        self.output_relay_polarity("NORMal", chan)

    # --- 11. SYSTem Commands ---
    def system_channel_count(self):
        return self.inst.query("SYSTem:CHANnel:COUNt?").strip()
    def system_model(self, chan=1):
        return self.inst.query(f"SYSTem:CHANnel:MODel? {_format_chanlist(chan)}").strip()
    def system_option(self, chan=1):
        return self.inst.query(f"SYSTem:CHANnel:OPTion? {_format_chanlist(chan)}").strip()
    def system_serial(self, chan=1):
        return self.inst.query(f"SYSTem:CHANnel:SERial? {_format_chanlist(chan)}").strip()
    def system_communicate_rlstate(self, state="LOCal"):
        self.inst.write(f"SYSTem:COMMunicate:RLSTate {state.upper()}")
    def system_tcpip_control(self):
        return self.inst.query("SYSTem:TCPip:CONTrol?").strip()
    def system_error(self):
        return self.inst.query("SYSTem:ERRor?").strip()
    def system_preset(self):
        self.inst.write("SYSTem:PRESet")
    def system_version(self):
        return self.inst.query("SYSTem:VERSion?").strip()
    def configure_system(self, chan=1):
        return {
            "channel_count": self.system_channel_count(),
            "model": self.system_model(chan),
            "option": self.system_option(chan),
            "serial": self.system_serial(chan),
            "version": self.system_version(),
        }

    # --- 12. STATus Commands ---
    def status_operation_event(self, chan=1):
        return self.inst.query(f"STATus:OPERation:EVENt? {_format_chanlist(chan)}").strip()
    def status_operation_condition(self, chan=1):
        return self.inst.query(f"STATus:OPERation:CONDition? {_format_chanlist(chan)}").strip()
    def status_operation_enable(self, value, chan=1):
        self.inst.write(f"STATus:OPERation:ENABle {value}, {_format_chanlist(chan)}")
    def status_operation_ntransition(self, value, chan=1):
        self.inst.write(f"STATus:OPERation:NTRansition {value}, {_format_chanlist(chan)}")
    def status_operation_ptransition(self, value, chan=1):
        self.inst.write(f"STATus:OPERation:PTRansition {value}, {_format_chanlist(chan)}")
    def status_operation_preset(self):
        self.inst.write("STATus:OPERation:PRESet")
    def status_questionable_event(self, chan=1):
        return self.inst.query(f"STATus:QUEStionable:EVENt? {_format_chanlist(chan)}").strip()
    def status_questionable_condition(self, chan=1):
        return self.inst.query(f"STATus:QUEStionable:CONDition? {_format_chanlist(chan)}").strip()
    def status_questionable_enable(self, value, chan=1):
        self.inst.write(f"STATus:QUEStionable:ENABle {value}, {_format_chanlist(chan)}")
    def status_questionable_ntransition(self, value, chan=1):
        self.inst.write(f"STATus:QUEStionable:NTRansition {value}, {_format_chanlist(chan)}")
    def status_questionable_ptransition(self, value, chan=1):
        self.inst.write(f"STATus:QUEStionable:PTRansition {value}, {_format_chanlist(chan)}")
    def configure_status(self, chan=1):
        return {
            "operation_event": self.status_operation_event(chan),
            "operation_condition": self.status_operation_condition(chan),
            "questionable_event": self.status_questionable_event(chan),
            "questionable_condition": self.status_questionable_condition(chan)
        }

    # --- 13. TRIGger Commands ---
    def trigger_acquire_immediate(self, chan=1):
        self.inst.write(f"TRIGger:ACQuire:IMMediate {_format_chanlist(chan)}")
    def trigger_current_level(self, value, chan=1):
        self.inst.write(f"TRIGger:CURRent:LEVel {value}, {_format_chanlist(chan)}")
    def trigger_current_slope(self, slope="POSitive", chan=1):
        self.inst.write(f"TRIGger:CURRent:SLOPe {slope.upper()}, {_format_chanlist(chan)}")
    def trigger_source(self, source="BUS", chan=1):
        self.inst.write(f"TRIGger:SOURce {source.upper()}, {_format_chanlist(chan)}")
    def trigger_voltage_level(self, value, chan=1):
        self.inst.write(f"TRIGger:VOLTage:LEVel {value}, {_format_chanlist(chan)}")
    def trigger_voltage_slope(self, slope="POSitive", chan=1):
        self.inst.write(f"TRIGger:VOLTage:SLOPe {slope.upper()}, {_format_chanlist(chan)}")
    def trigger_elog_immediate(self, chan=1):
        self.inst.write(f"TRIGger:ELOG:IMMediate {_format_chanlist(chan)}")
    def trigger_elog_source(self, source="IMMediate", chan=1):
        self.inst.write(f"TRIGger:ELOG:SOURce {source.upper()}, {_format_chanlist(chan)}")
    def trigger_transient_immediate(self, chan=1):
        self.inst.write(f"TRIGger:TRANsient:IMMediate {_format_chanlist(chan)}")
    def trigger_transient_source(self, source="IMMediate", chan=1):
        self.inst.write(f"TRIGger:TRANsient:SOURce {source.upper()}, {_format_chanlist(chan)}")
    def configure_trigger(self, chan=1, current_level=1.0, voltage_level=5.0, current_slope="POSitive", voltage_slope="POSitive", source="BUS"):
        self.trigger_current_level(current_level, chan)
        self.trigger_current_slope(current_slope, chan)
        self.trigger_voltage_level(voltage_level, chan)
        self.trigger_voltage_slope(voltage_slope, chan)
        self.trigger_source(source, chan)

# -------------------
# Example usage:
# -------------------
# rm = pyvisa.ResourceManager()
# inst = rm.open_resource("USB0::0x2A8D::0x1401::MY57200246::INSTR")
# n67 = N67xxSCPI(inst)
# n67.configure_abort()
# n67.configure_calibrate()
# n67.configure_common()
# n67.configure_display()
# n67.configure_fetch()
# n67.configure_format()
# n67.configure_initiate()
# n67.configure_output()
# n67.configure_sense()
# n67.configure_source()
# n67.configure_system()
# n67.configure_status()
# n67.configure_trigger()
# inst.close()
