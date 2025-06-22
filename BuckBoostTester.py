import time
import numpy as np
import matplotlib.pyplot as plt
import csv

class TPS63070TestFramework:
    def __init__(self, psu, dmm, scope, load, ps_sync_control):
        self.psu = psu
        self.dmm = dmm
        self.scope = scope
        self.load = load
        self.ps_sync_control = ps_sync_control

    def set_ps_sync(self, state):
        print(f"Setting PS/SYNC to {state}")
        self.ps_sync_control(state)
        time.sleep(0.5)

    def power_up(self, vin, current_limit=2.0):
        self.psu.set_voltage(1, vin)
        self.psu.set_current(1, current_limit)
        self.psu.output_on(1)
        time.sleep(1)

    def power_down(self):
        self.psu.output_off(1)
        self.load.turn_off()

    def measure_basic_params(self):
        vin = self.psu.measure_voltage(1)
        iin = self.psu.measure_current(1)
        vout = self.dmm.measure_voltage_dc()
        iout = self.dmm.measure_current_dc()
        rload = self.dmm.measure_resistance()
        print(f"VIN={vin:.3f} V, IIN={iin:.3f} A, VOUT={vout:.3f} V, IOUT={iout:.3f} A, RLOAD={rload:.1f} Ohm")
        return vin, iin, vout, iout, rload

    def calculate_efficiency(self, vin, iin, vout, iout):
        pin = vin * iin
        pout = vout * iout
        efficiency = (pout / pin) * 100 if pin > 0 else 0
        print(f"Efficiency: {efficiency:.2f} %")
        return efficiency

    def sweep_efficiency(self, vin_list, vout_target, ps_sync_state, mode, current_points):
        results = []
        for vin in vin_list:
            print(f"\nEfficiency Sweep: VIN={vin} V, VOUT={vout_target} V, PS/SYNC={ps_sync_state}, Mode={mode}")
            self.set_ps_sync(ps_sync_state)
            self.power_up(vin)
            self.load.turn_on()
            for iout in current_points:
                self.load.set_current(iout)
                time.sleep(0.5)
                vin_meas, iin_meas, vout_meas, iout_meas, _ = self.measure_basic_params()
                eff = self.calculate_efficiency(vin_meas, iin_meas, vout_meas, iout_meas)
                results.append({'VIN': vin_meas, 'VOUT_Target': vout_target, 'PS_SYNC': ps_sync_state,
                                'Mode': mode, 'Load_Current_A': iout_meas, 'Efficiency_%': eff})
            self.load.turn_off()
            self.power_down()
        return results

    def sweep_load_regulation(self, vin_list, vout_target, ps_sync_state, mode, current_points):
        results = []
        for vin in vin_list:
            print(f"\nLoad Regulation: VIN={vin} V, VOUT={vout_target} V, PS/SYNC={ps_sync_state}, Mode={mode}")
            self.set_ps_sync(ps_sync_state)
            self.power_up(vin)
            self.load.turn_on()
            for iout in current_points:
                self.load.set_current(iout)
                time.sleep(0.5)
                vout_meas = self.dmm.measure_voltage_dc()
                print(f"Load {iout:.2f} A, VOUT: {vout_meas:.3f} V")
                results.append({'VIN': vin, 'VOUT_Target': vout_target, 'PS_SYNC': ps_sync_state,
                                'Mode': mode, 'Load_Current_A': iout, 'Output_Voltage_V': vout_meas})
            self.load.turn_off()
            self.power_down()
        return results

    def capture_load_transient(self, vin, vout_target, ps_sync_state, mode, load_steps, step_duration=0.1):
        print(f"\nLoad Transient Test: VIN={vin} V, VOUT={vout_target} V, PS/SYNC={ps_sync_state}, Mode={mode}")
        self.set_ps_sync(ps_sync_state)
        self.power_up(vin)
        self.load.turn_on()
        self.scope.set_channel(1, display=True, scale=0.5, position=0, coupling='DC')
        self.scope.set_timebase(5e-6)
        self.scope.set_trigger_edge(1, slope='POS', level=0.1)

        transient_waveforms = []
        for i in range(len(load_steps) - 1):
            self.load.set_current(load_steps[i])
            time.sleep(step_duration)
            self.load.set_current(load_steps[i+1])
            time.sleep(step_duration)
            if self.scope.wait_for_trigger(timeout=5):
                times, volts = self.scope.fetch_waveform(1)
                transient_waveforms.append({'Load_Step': (load_steps[i], load_steps[i+1]), 'Times': times, 'Voltages': volts})
                print(f"Captured load transient from {load_steps[i]} A to {load_steps[i+1]} A")
            else:
                print("Trigger timeout during load transient capture")
        self.load.turn_off()
        self.power_down()
        return transient_waveforms

    def capture_line_transient(self, vin_steps, vout_target, load_current, ps_sync_state, mode):
        print(f"\nLine Transient Test: VOUT={vout_target} V, Load={load_current} A, PS/SYNC={ps_sync_state}, Mode={mode}")
        self.set_ps_sync(ps_sync_state)
        self.load.set_current(load_current)
        self.load.turn_on()
        self.scope.set_channel(1, display=True, scale=0.5, position=0, coupling='DC')
        self.scope.set_timebase(5e-6)
        self.scope.set_trigger_edge(1, slope='POS', level=0.1)

        transient_waveforms = []
        for vin in vin_steps:
            self.psu.set_voltage(1, vin)
            self.psu.set_current(1, 2.0)
            self.psu.output_on(1)
            time.sleep(0.1)
            if self.scope.wait_for_trigger(timeout=5):
                times, volts = self.scope.fetch_waveform(1)
                transient_waveforms.append({'VIN': vin, 'Times': times, 'Voltages': volts})
                print(f"Captured line transient at VIN={vin} V")
            else:
                print("Trigger timeout during line transient capture")
        self.load.turn_off()
        self.power_down()
        return transient_waveforms

    def measure_output_ripple(self, vin_list, vout_target, load_current, ps_sync_state, mode, channel=1):
        print(f"\nOutput Ripple Measurement: VOUT={vout_target} V, Load={load_current} A, PS/SYNC={ps_sync_state}, Mode={mode}")
        results = []
        for vin in vin_list:
            self.set_ps_sync(ps_sync_state)
            self.power_up(vin)
            self.load.set_current(load_current)
            self.load.turn_on()
            time.sleep(1)
            self.scope.set_channel(channel, display=True, scale=0.02, position=0, coupling='AC')
            self.scope.set_timebase(2e-6)
            self.scope.set_trigger_edge(channel, slope='POS', level=0.1)
            if self.scope.wait_for_trigger(timeout=5):
                _, volts = self.scope.fetch_waveform(channel)
                volts = np.array(volts)
                ripple_vpp = volts.max() - volts.min()
                print(f"Ripple Vpp: {ripple_vpp*1000:.2f} mV")
                results.append({'VIN': vin, 'VOUT_Target': vout_target, 'Load_Current_A': load_current, 'Ripple_Vpp_V': ripple_vpp})
            else:
                print("Trigger timeout on ripple measurement.")
                results.append({'VIN': vin, 'VOUT_Target': vout_target, 'Load_Current_A': load_current, 'Ripple_Vpp_V': None})
            self.load.turn_off()
            self.power_down()
        return results

    def plot_results(self, data, x_key, y_key, title, xlabel, ylabel, filename=None):
        grouped = {}
        for d in data:
            key = (d.get('VIN'), d.get('VOUT_Target'), d.get('PS_SYNC'), d.get('Mode'))
            grouped.setdefault(key, []).append(d)
        plt.figure(figsize=(8,6))
        for key, points in grouped.items():
            points = sorted(points, key=lambda x: x[x_key])
            x = [p[x_key] for p in points]
            y = [p[y_key] for p in points]
            label = f"VIN={key[0]}V, VOUT={key[1]}V, PS/SYNC={key[2]}, Mode={key[3]}"
            plt.plot(x, y, marker='o', label=label)
        plt.title(title)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.grid(True)
        plt.legend()
        if filename:
            plt.savefig(filename)
            print(f"Plot saved to {filename}")
        plt.show()

    def save_csv(self, data, filename):
        keys = data[0].keys()
        with open(filename, 'w', newline='') as f:
            writer = csv.DictWriter(f, keys)
            writer.writeheader()
            writer.writerows(data)
        print(f"Data saved to {filename}")

# --- Usage Example ---

if __name__ == "__main__":
    from your_n670x_module import KeysightN670x
    from your_34461a_module import Keysight34461A
    from your_scope_module import TektronixDPO2014B
    from your_load_module import ElectronicLoad

    def ps_sync_control(state):
        print(f"PS/SYNC pin set to {state}")
        # Implement hardware-specific control here

    psu = KeysightN670x('USB0::0x2A8D::0x0F02::MY56002702::INSTR')
    dmm = Keysight34461A('USB0::0x0957::0x0607::MY1234567::INSTR')
    scope = TektronixDPO2014B('USB0::0x0699::0x0363::C010101::INSTR')
    load = ElectronicLoad('GPIB::5')

    tester = TPS63070TestFramework(psu, dmm, scope, load, ps_sync_control)

    vin_values = [3, 4.2, 5, 7, 9, 12]
    current_points = np.linspace(0.1, 2.0, 20)

    # Efficiency curves PFM/PWM mode, VOUT=7V, PS/SYNC=Low
    efficiency_data = tester.sweep_efficiency(vin_values, 7, 'Low', 'PFM/PWM', current_points)
    tester.save_csv(efficiency_data, "efficiency_pfm_pwm_7V.csv")
    tester.plot_results(efficiency_data, 'Load_Current_A', 'Efficiency_%', 'Efficiency vs Output Current (PFM/PWM) VOUT=7V PS/SYNC=Low', 'Output Current (A)', 'Efficiency (%)')

    # Load regulation PWM mode, VOUT=7V, PS/SYNC=High
    load_reg_data = tester.sweep_load_regulation(vin_values, 7, 'High', 'PWM only', current_points)
    tester.save_csv(load_reg_data, "load_regulation_pwm_7V.csv")
    tester.plot_results(load_reg_data, 'Load_Current_A', 'Output_Voltage_V', 'Load Regulation VOUT=7V PS/SYNC=High', 'Load Current (A)', 'Output Voltage (V)')

    # Load transient test example
    load_steps = [0.1, 1.0]
    load_transient_data = tester.capture_load_transient(5, 7, 'Low', 'PFM/PWM', load_steps)
    # Process load_transient_data as needed (plot waveforms, analyze transient metrics)

    # Line transient test example
    vin_steps = np.linspace(5, 9, 5)
    line_transient_data = tester.capture_line_transient(vin_steps, 7, 1.0, 'Low', 'PFM/PWM')
    # Process line_transient_data as needed

    # Output ripple measurement example
    ripple_data = tester.measure_output_ripple([5, 12], 7, 0.3, 'Low', 'PFM/PWM')
    tester.save_csv(ripple_data, "output_ripple.csv")
    tester.plot_results(ripple_data, 'VIN', 'Ripple_Vpp_V', 'Output Voltage Ripple', 'Input Voltage (V)', 'Ripple (Vpp)')

    # Close instruments
    psu.close()
    dmm.close()
    scope.close()
    load.close()
