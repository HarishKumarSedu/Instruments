import time
import pyvisa as visa

class N670x:
    """
    Keysight N670x Series Power Supply SCPI Control Library.
    Combines basic and advanced application functionalities.
    """

    def __init__(self, port='USB0::0x2A8D::0x0F02::MY56002702::INSTR'):
        rm = visa.ResourceManager()
        self.my_instr = rm.open_resource(port)
        self.my_instr.read_termination = '\n'
        self.my_instr.write_termination = '\n'
        self.channel = {1: "OUT1", 2: "OUT2", 3: "OUT3", 4: "OUT4"}

    # === Basic Instrument Functions ===

    def get_IDN(self):
        """Query instrument identification string. SCPI: *IDN?"""
        self.my_instr.write('SYST:REM')
        time.sleep(1)
        return self.my_instr.query('*IDN?')

    def reset(self):
        """Reset the instrument. SCPI: *RST"""
        self.my_instr.write('*RST')

    def clear_errors(self):
        """Clear error queue. SCPI: *CLS"""
        self.my_instr.write('*CLS')

    def errorLog(self):
        """Query error queue. SCPI: SYST:ERR?"""
        return self.my_instr.query('SYST:ERR?')

    def modelNumber(self, channel: int):
        """Query model number of a channel. SCPI: SYST:CHAN:MOD? (@n)"""
        return self.my_instr.query(f'SYST:CHAN:MOD? (@{channel})')

    def serialNumber(self, channel: int):
        """Query serial number of a channel. SCPI: SYST:CHAN:SER? (@n)"""
        return self.my_instr.query(f'SYST:CHAN:SER? (@{channel})')

    def installedOptions(self, channel: int):
        """Query installed options for a channel. SCPI: SYST:CHAN:OPT? (@n)"""
        return self.my_instr.query(f'SYST:CHAN:OPT? (@{channel})')

    def outp_ON(self, channel: int):
        """Turn ON output for a channel. SCPI: OUTP ON,(@n)"""
        self.my_instr.write(f'OUTP ON,(@{channel})')

    def outp_OFF(self, channel: int):
        """Turn OFF output for a channel. SCPI: OUTP OFF,(@n)"""
        self.my_instr.write(f'OUTP OFF,(@{channel})')

    def getOutStatus(self):
        """Query output status of all channels. SCPI: OUTP:STAT?"""
        return self.my_instr.query('OUTP:STAT?')

    def setVoltage(self, channel: int, voltage: float):
        """Set output voltage. SCPI: VOLT <level>,(@n)"""
        self.my_instr.write(f'VOLT {voltage},(@{channel})')

    def setCurrent(self, channel: int, current: float):
        """Set output current. SCPI: CURR <level>,(@n)"""
        self.my_instr.write(f'CURR {current},(@{channel})')

    def setRange_Voltage(self, channel: int, voltageRange: float):
        """Set voltage range. SCPI: VOLT:RANG <range>,(@n)"""
        self.my_instr.write(f'VOLT:RANG {voltageRange},(@{channel})')

    def setRange_Current(self, channel: int, currentRange: float):
        """Set current range. SCPI: CURR:RANG <range>,(@n)"""
        self.my_instr.write(f'CURR:RANG {currentRange},(@{channel})')

    def setCurrentMode(self, channel: int):
        """Set channel to current priority mode. SCPI: OUTP:PMOD CURR,(@n)"""
        self.my_instr.write(f'OUTP:PMOD CURR,(@{channel})')

    def setVoltageMode(self, channel: int):
        """Set channel to voltage priority mode. SCPI: OUTP:PMOD VOLT,(@n)"""
        self.my_instr.write(f'OUTP:PMOD VOLT,(@{channel})')

    def setReverseRelay_Polarity(self, channel: int):
        """Reverse relay polarity (Option 760). SCPI: OUTP:REL:POL REV,(@n)"""
        self.my_instr.write(f'OUTP:REL:POL REV,(@{channel})')

    def setNormalRelay_Polarity(self, channel: int):
        """Set relay polarity to normal. SCPI: OUTP:REL:POL NORM,(@n)"""
        self.my_instr.write(f'OUTP:REL:POL NORM,(@{channel})')

    def setCurrent_Positive_Limit(self, channel: int, current: float):
        """Set positive current limit. SCPI: CURR:LIM <value>,(@n)"""
        self.my_instr.write(f'CURR:LIM {current},(@{channel})')

    def setCurrent_Negative_Limit(self, channel: int, current: float):
        """Set negative current limit. SCPI: CURR:LIM:COUP OFF,(@n); CURR:LIM:NEG <value>,(@n)"""
        self.my_instr.write(f'CURR:LIM:COUP OFF,(@{channel})')
        self.my_instr.write(f'CURR:LIM:NEG {current},(@{channel})')

    def setVoltage_Priority(self, channel: int):
        """Set voltage priority mode. SCPI: FUNC VOLT,(@n)"""
        self.my_instr.write(f'FUNC VOLT,(@{channel})')

    def setCurrent_Priority(self, channel: int):
        """Set current priority mode. SCPI: FUNC CURR,(@n)"""
        self.my_instr.write(f'FUNC CURR,(@{channel})')

    def setTurn_ON_Delay(self, channel: int, delay: float):
        """Set turn-on delay (s). SCPI: OUTP:DEL:RISE <delay>,(@n)"""
        self.my_instr.write(f'OUTP:DEL:RISE {delay},(@{channel})')

    def setTurn_OFF_Delay(self, channel: int, delay: float):
        """Set turn-off delay (s). SCPI: OUTP:DEL:FALL <delay>,(@n)"""
        self.my_instr.write(f'OUTP:DEL:FALL {delay},(@{channel})')

    def setOVP_Protection(self, channel: int, OVP: float):
        """Set OVP level. SCPI: VOLT:PROT <level>,(@n)"""
        self.my_instr.write(f'VOLT:PROT {OVP},(@{channel})')

    def setOCP_Protection(self, channel: int, state: bool):
        """Enable/disable OCP. SCPI: CURR:PROT:STAT ON|OFF,(@n)"""
        val = 'ON' if state else 'OFF'
        self.my_instr.write(f'CURR:PROT:STAT {val},(@{channel})')

    def setOCP_Delay(self, channel: int, delay: float):
        """Set OCP delay (s). SCPI: CURR:PROT:DEL <delay>,(@n)"""
        self.my_instr.write(f'CURR:PROT:DEL {delay},(@{channel})')

    def setOutput_Protection_Coupling_ON(self):
        """Enable output protection coupling. SCPI: OUTP:PROT:COUP ON"""
        self.my_instr.write('OUTP:PROT:COUP ON')

    def setOutput_Current_Protection_ON(self, channel: int):
        """Enable output current protection. SCPI: CURR:PROT:STAT ON,(@n)"""
        self.my_instr.write(f'CURR:PROT:STAT ON,(@{channel})')

    def setOutput_Current_Protection_OFF(self, channel: int):
        """Disable output current protection. SCPI: CURR:PROT:STAT OFF,(@n)"""
        self.my_instr.write(f'CURR:PROT:STAT OFF,(@{channel})')

    def setOutput_Voltage_Protection_ON(self, channel: int):
        """Enable output voltage protection. SCPI: VOLT:PROT:STAT ON,(@n)"""
        self.my_instr.write(f'VOLT:PROT:STAT ON,(@{channel})')

    def setOutput_Voltage_Protection_OFF(self, channel: int):
        """Disable output voltage protection. SCPI: VOLT:PROT:STAT OFF,(@n)"""
        self.my_instr.write(f'VOLT:PROT:STAT OFF,(@{channel})')

    def clearOutput_Protection_Clear(self, channel: int):
        """Clear output protection fault. SCPI: OUTP:PROT:CLE (@n)"""
        self.my_instr.write(f'OUTP:PROT:CLE (@{channel})')

    def protection_Status_Current(self):
        """Query current protection status. SCPI: CURRent:PROTection:STATe?"""
        return self.my_instr.query('CURRent:PROTection:STATe?')

    def protection_Status_Voltage(self):
        """Query voltage protection status. SCPI: VOLTage:PROTection:STATe?"""
        return self.my_instr.query('VOLTage:PROTection:STATe?')

    def measureVoltage(self, channel: int):
        """Measure output voltage. SCPI: MEAS:VOLT? (@n)"""
        return float(self.my_instr.query(f'MEAS:VOLT? (@{channel})'))

    def measureCurrent(self, channel: int):
        """Measure output current. SCPI: MEAS:CURR? (@n)"""
        return float(self.my_instr.query(f'MEAS:CURR? (@{channel})'))

    # === Advanced Application Functions ===

    # --- Output Impedance ---
    def set_output_impedance(self, channel: int, impedance: float):
        """Set output impedance (Ohms). SCPI: OUTP:IMP {impedance},(@n)"""
        self.my_instr.write(f'OUTP:IMP {impedance},(@{channel})')

    def disable_output_impedance(self, channel: int):
        """Disable output impedance simulation. SCPI: OUTP:IMP 0,(@n)"""
        self.my_instr.write(f'OUTP:IMP 0,(@{channel})')

    # --- Regulation Measurement ---
    def measure_load_regulation(self, channel: int, load_step: float):
        """
        Measure load regulation. (Custom sequence, see manual)
        Typically: step load, measure voltage before/after, calculate deviation.
        """
        v1 = self.measureVoltage(channel)
        self.setCurrent(channel, load_step)
        time.sleep(0.5)
        v2 = self.measureVoltage(channel)
        self.setCurrent(channel, 0)
        return (v2 - v1) / v1 * 100  # % deviation

    def measure_line_regulation(self, channel: int, line_step: float):
        """
        Measure line regulation. (Custom sequence, see manual)
        Typically: step input line, measure output voltage before/after, calculate deviation.
        """
        # This is typically performed via hardware, so here we just simulate the call.
        v1 = self.measureVoltage(channel)
        # User must change line voltage externally
        input("Change AC line voltage, then press Enter...")
        v2 = self.measureVoltage(channel)
        return (v2 - v1) / v1 * 100  # % deviation

    # --- Quadrant Operation ---
    def set_operation_quadrant(self, channel: int, quadrant: int):
        """
        Set operation quadrant (1=Source, 2=Sink, 3=Source/Sink, 4=Passive).
        SCPI: SOUR:QUAD {quadrant},(@n)
        """
        self.my_instr.write(f'SOUR:QUAD {quadrant},(@{channel})')

    # --- Emulation Modes ---
    def enable_battery_emulation(self, channel: int, voltage: float, resistance: float):
        """
        Enable battery emulation.
        SCPI: BATTERY:EMUL ON,(@n); BATTERY:VOLT {voltage},(@n); BATTERY:RES {resistance},(@n)
        """
        self.my_instr.write(f'BATTERY:EMUL ON,(@{channel})')
        self.my_instr.write(f'BATTERY:VOLT {voltage},(@{channel})')
        self.my_instr.write(f'BATTERY:RES {resistance},(@{channel})')

    def enable_solar_emulation(self, channel: int, irradiance: float, temp: float):
        """
        Enable solar panel emulation.
        SCPI: SOLAR:EMUL ON,(@n); SOLAR:IRR {irradiance},(@n); SOLAR:TEMP {temp},(@n)
        """
        self.my_instr.write(f'SOLAR:EMUL ON,(@{channel})')
        self.my_instr.write(f'SOLAR:IRR {irradiance},(@{channel})')
        self.my_instr.write(f'SOLAR:TEMP {temp},(@{channel})')

    # --- Application Setups ---
    def init_standard_setup(self, channel: int):
        """
        Standard setup: remote, default protection, averaging.
        """
        self.my_instr.write('SYST:REM')
        time.sleep(0.5)
        self.my_instr.write(f'VOLT:PROT:STAT ON,(@{channel})')
        self.my_instr.write(f'CURR:PROT:STAT ON,(@{channel})')
        self.my_instr.write(f'SENS:AVER:COUN 10,(@{channel})')

    def init_dynamic_load_setup(self, channel: int, max_current: float):
        """
        Dynamic load test setup.
        """
        self.my_instr.write(f'CURR:SINK:STAT ON,(@{channel})')
        self.my_instr.write(f'SOUR:FUNC:MODE TRAN,(@{channel})')
        self.my_instr.write(f'SOUR:CURR:SLEW 0.1,(@{channel})')
        self.my_instr.write(f'CURR:LIM {max_current},(@{channel})')

    def init_battery_test_setup(self, channel: int):
        """
        Battery test setup.
        """
        self.my_instr.write(f'BATTERY:EMUL ON,(@{channel})')
        self.my_instr.write(f'BATTERY:CYC:STAT ON,(@{channel})')
        self.my_instr.write(f'BATTERY:TERM:CURR 0.1,(@{channel})')

    # --- Save/Recall Setup ---
    def save_setup(self, slot: int):
        """Save current setup. SCPI: *SAV {slot}"""
        self.my_instr.write(f'*SAV {slot}')

    def recall_setup(self, slot: int):
        """Recall setup. SCPI: *RCL {slot}"""
        self.my_instr.write(f'*RCL {slot}')

    # --- Close VISA ---
    def close(self):
        """Close VISA session."""
        self.my_instr.close()
        # --- ARB Sequence Control ---
    def arb_select_voltage(self, channel: int):
        """Set ARB function type to voltage. SCPI: ARB:FUNC:TYPE VOLT,(@n)"""
        self.my_instr.write(f'ARB:FUNC:TYPE VOLT,(@{channel})')

    def arb_select_current(self, channel: int):
        """Set ARB function type to current. SCPI: ARB:FUNC:TYPE CURR,(@n)"""
        self.my_instr.write(f'ARB:FUNC:TYPE CURR,(@{channel})')

    def arb_set_sequence(self, channel: int):
        """Set ARB function shape to sequence. SCPI: ARB:FUNC:SHAP SEQ,(@n)"""
        self.my_instr.write(f'ARB:FUNC:SHAP SEQ,(@{channel})')

    def arb_reset_sequence(self, channel: int):
        """Reset ARB sequence. SCPI: ARB:SEQ:RES(@n)"""
        self.my_instr.write(f'ARB:SEQ:RES(@{channel})')

    def arb_set_last_value_on(self, channel: int):
        """Hold last ARB value after completion. SCPI: ARB:TERM:LAST ON,(@n)"""
        self.my_instr.write(f'ARB:TERM:LAST ON,(@{channel})')

    def arb_set_last_value_off(self, channel: int):
        """Return to DC value after ARB. SCPI: ARB:TERM:LAST OFF,(@n)"""
        self.my_instr.write(f'ARB:TERM:LAST OFF,(@{channel})')

    def arb_trigger(self):
        """Trigger ARB waveform. SCPI: *TRG"""
        self.my_instr.write('*TRG')

    # --- ARB Pulse Waveforms ---
    def arb_pulse_voltage(self, channel: int, v_start: float, v_top: float, t_start: float, t_top: float, t_end: float):
        """Program voltage pulse ARB waveform."""
        self.my_instr.write(f'ARB:VOLT:PULS:STAR {v_start},(@{channel})')
        self.my_instr.write(f'ARB:VOLT:PULS:TOP {v_top},(@{channel})')
        self.my_instr.write(f'ARB:VOLT:PULS:STAR:TIM {t_start},(@{channel})')
        self.my_instr.write(f'ARB:VOLT:PULS:TOP:TIM {t_top},(@{channel})')
        self.my_instr.write(f'ARB:VOLT:PULS:END:TIM {t_end},(@{channel})')

    def arb_pulse_current(self, channel: int, i_start: float, i_top: float, t_start: float, t_top: float, t_end: float):
        """Program current pulse ARB waveform."""
        self.my_instr.write(f'ARB:CURR:PULS:STAR {i_start},(@{channel})')
        self.my_instr.write(f'ARB:CURR:PULS:TOP {i_top},(@{channel})')
        self.my_instr.write(f'ARB:CURR:PULS:STAR:TIM {t_start},(@{channel})')
        self.my_instr.write(f'ARB:CURR:PULS:TOP:TIM {t_top},(@{channel})')
        self.my_instr.write(f'ARB:CURR:PULS:END:TIM {t_end},(@{channel})')

    # --- ARB Step Waveforms ---
    def arb_step_voltage(self, channel: int, v_start: float, v_end: float, t_start: float):
        """Program voltage step ARB waveform."""
        self.my_instr.write(f'ARB:VOLT:STEP:STAR {v_start},(@{channel})')
        self.my_instr.write(f'ARB:VOLT:STEP:END {v_end},(@{channel})')
        self.my_instr.write(f'ARB:VOLT:STEP:STAR:TIM {t_start},(@{channel})')

    def arb_step_current(self, channel: int, i_start: float, i_end: float, t_start: float):
        """Program current step ARB waveform."""
        self.my_instr.write(f'ARB:CURR:STEP:STAR {i_start},(@{channel})')
        self.my_instr.write(f'ARB:CURR:STEP:END {i_end},(@{channel})')
        self.my_instr.write(f'ARB:CURR:STEP:STAR:TIM {t_start},(@{channel})')

    # --- ARB Ramp Waveforms ---
    def arb_ramp_voltage(self, channel: int, v_start: float, v_end: float, t_start: float, t_rise: float, t_end: float):
        """Program voltage ramp ARB waveform."""
        self.my_instr.write(f'ARB:VOLT:RAMP:STAR {v_start},(@{channel})')
        self.my_instr.write(f'ARB:VOLT:RAMP:END {v_end},(@{channel})')
        self.my_instr.write(f'ARB:VOLT:RAMP:STAR:TIM {t_start},(@{channel})')
        self.my_instr.write(f'ARB:VOLT:RAMP:RTIM {t_rise},(@{channel})')
        self.my_instr.write(f'ARB:VOLT:RAMP:END:TIM {t_end},(@{channel})')

    def arb_ramp_current(self, channel: int, i_start: float, i_end: float, t_start: float, t_rise: float, t_end: float):
        """Program current ramp ARB waveform."""
        self.my_instr.write(f'ARB:CURR:RAMP:STAR {i_start},(@{channel})')
        self.my_instr.write(f'ARB:CURR:RAMP:END {i_end},(@{channel})')
        self.my_instr.write(f'ARB:CURR:RAMP:STAR:TIM {t_start},(@{channel})')
        self.my_instr.write(f'ARB:CURR:RAMP:RTIM {t_rise},(@{channel})')
        self.my_instr.write(f'ARB:CURR:RAMP:END:TIM {t_end},(@{channel})')

    # --- ARB Staircase Waveforms ---
    def arb_staircase_voltage(self, channel: int, steps: int, v_start: float, v_end: float, t_start: float, t_step: float, t_end: float):
        """Program voltage staircase ARB waveform."""
        self.my_instr.write(f'ARB:VOLT:STA:STAR {v_start},(@{channel})')
        self.my_instr.write(f'ARB:VOLT:STA:END {v_end},(@{channel})')
        self.my_instr.write(f'ARB:VOLT:STA:STAR:TIM {t_start},(@{channel})')
        self.my_instr.write(f'ARB:VOLT:STA:TIM {t_step},(@{channel})')
        self.my_instr.write(f'ARB:VOLT:STA:END:TIM {t_end},(@{channel})')
        self.my_instr.write(f'ARB:VOLT:STA:NST {steps},(@{channel})')

    def arb_staircase_current(self, channel: int, steps: int, i_start: float, i_end: float, t_start: float, t_step: float, t_end: float):
        """Program current staircase ARB waveform."""
        self.my_instr.write(f'ARB:CURR:STA:STAR {i_start},(@{channel})')
        self.my_instr.write(f'ARB:CURR:STA:END {i_end},(@{channel})')
        self.my_instr.write(f'ARB:CURR:STA:STAR:TIM {t_start},(@{channel})')
        self.my_instr.write(f'ARB:CURR:STA:TIM {t_step},(@{channel})')
        self.my_instr.write(f'ARB:CURR:STA:END:TIM {t_end},(@{channel})')
        self.my_instr.write(f'ARB:CURR:STA:NST {steps},(@{channel})')

    # --- ARB Trapezoid Waveforms ---
    def arb_trapezoid_voltage(self, channel: int, v_start: float, v_end: float, t_start: float, t_rise: float, t_top: float, t_fall: float, t_end: float):
        """Program voltage trapezoid ARB waveform."""
        self.my_instr.write(f'ARB:VOLT:TRAP:STAR {v_start},(@{channel})')
        self.my_instr.write(f'ARB:VOLT:TRAP:END {v_end},(@{channel})')
        self.my_instr.write(f'ARB:VOLT:TRAP:STAR:TIM {t_start},(@{channel})')
        self.my_instr.write(f'ARB:VOLT:TRAP:RTIM {t_rise},(@{channel})')
        self.my_instr.write(f'ARB:VOLT:TRAP:TOP:TIM {t_top},(@{channel})')
        self.my_instr.write(f'ARB:VOLT:TRAP:FTIM {t_fall},(@{channel})')
        self.my_instr.write(f'ARB:VOLT:TRAP:END:TIM {t_end},(@{channel})')

    def arb_trapezoid_current(self, channel: int, i_start: float, i_end: float, t_start: float, t_rise: float, t_top: float, t_fall: float, t_end: float):
        """Program current trapezoid ARB waveform."""
        self.my_instr.write(f'ARB:CURR:TRAP:STAR {i_start},(@{channel})')
        self.my_instr.write(f'ARB:CURR:TRAP:END {i_end},(@{channel})')
        self.my_instr.write(f'ARB:CURR:TRAP:STAR:TIM {t_start},(@{channel})')
        self.my_instr.write(f'ARB:CURR:TRAP:RTIM {t_rise},(@{channel})')
        self.my_instr.write(f'ARB:CURR:TRAP:TOP:TIM {t_top},(@{channel})')
        self.my_instr.write(f'ARB:CURR:TRAP:FTIM {t_fall},(@{channel})')
        self.my_instr.write(f'ARB:CURR:TRAP:END:TIM {t_end},(@{channel})')
        
    def arb_Sine__Voltage(self, channel:int, amplitude:float, frequency:float, offset:float,
                          initial_Voltage:float, end_Voltage:float, initial_Time:float, end_Time:float):
        """
        Program a sine voltage ARB waveform.
        amplitude: Peak amplitude of sine (V)
        frequency: Frequency in Hz
        offset: DC offset (V)
        initial_Voltage: Start voltage (V)
        end_Voltage: End voltage (V)
        initial_Time: Start time (s)
        end_Time: End time (s)
        """
        self.my_instr.write(f'ARB:VOLT:SIN:AMP {amplitude},(@{channel})')
        self.my_instr.write(f'ARB:VOLT:SIN:FREQ {frequency},(@{channel})')
        self.my_instr.write(f'ARB:VOLT:SIN:OFFS {offset},(@{channel})')
        self.my_instr.write(f'ARB:VOLT:SIN:STAR {initial_Voltage},(@{channel})')
        self.my_instr.write(f'ARB:VOLT:SIN:END {end_Voltage},(@{channel})')
        self.my_instr.write(f'ARB:VOLT:SIN:STAR:TIM {initial_Time},(@{channel})')
        self.my_instr.write(f'ARB:VOLT:SIN:END:TIM {end_Time},(@{channel})')

    def arb_Sine__Current(self, channel:int, amplitude:float, frequency:float, offset:float,
                          initial_Current:float, end_Current:float, initial_Time:float, end_Time:float):
        """
        Program a sine current ARB waveform.
        amplitude: Peak amplitude of sine (A)
        frequency: Frequency in Hz
        offset: DC offset (A)
        initial_Current: Start current (A)
        end_Current: End current (A)
        initial_Time: Start time (s)
        end_Time: End time (s)
        """
        self.my_instr.write(f'ARB:CURR:SIN:AMP {amplitude},(@{channel})')
        self.my_instr.write(f'ARB:CURR:SIN:FREQ {frequency},(@{channel})')
        self.my_instr.write(f'ARB:CURR:SIN:OFFS {offset},(@{channel})')
        self.my_instr.write(f'ARB:CURR:SIN:STAR {initial_Current},(@{channel})')
        self.my_instr.write(f'ARB:CURR:SIN:END {end_Current},(@{channel})')
        self.my_instr.write(f'ARB:CURR:SIN:STAR:TIM {initial_Time},(@{channel})')
        self.my_instr.write(f'ARB:CURR:SIN:END:TIM {end_Time},(@{channel})')
