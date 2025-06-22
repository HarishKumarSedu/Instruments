import time
import csv

class N670xATE:
    """
    Automated Test Equipment (ATE) Application Class for Keysight N670x Power Supplies.
    Wraps the N670x instrument control class and provides a wide variety of test routines.
    """

    def __init__(self, psu):
        """
        Initialize with an instance of the N670x instrument control class.
        :param psu: Instance of N670x class controlling the instrument.
        """
        self.psu = psu

    # --- Basic Functionality Test ---
    def run_basic_functionality_test(self, channel=1):
        print("=== Basic Functionality Test ===")
        print("Instrument ID:", self.psu.get_IDN())
        self.psu.reset()
        self.psu.clear_errors()

        self.psu.setVoltage(channel, 5.0)
        self.psu.setCurrent(channel, 1.0)
        self.psu.setOVP_Protection(channel, 6.0)
        self.psu.setOCP_Protection(channel, True)
        self.psu.setOCP_Delay(channel, 0.1)

        self.psu.outp_ON(channel)
        time.sleep(1)
        v_meas = self.psu.measureVoltage(channel)
        i_meas = self.psu.measureCurrent(channel)
        print(f"Measured Voltage: {v_meas:.3f} V")
        print(f"Measured Current: {i_meas:.3f} A")

        self.psu.outp_OFF(channel)
        print("Output turned OFF")
        print("Error log:", self.psu.errorLog())
        print("=== Basic Functionality Test Complete ===\n")

    # --- Protection Tests ---
    def run_OVP_protection_test(self, channel=1):
        print("=== OVP Protection Test ===")
        self.psu.reset()
        self.psu.clear_errors()
        self.psu.setVoltage(channel, 5.0)
        self.psu.setOVP_Protection(channel, 5.5)
        self.psu.outp_ON(channel)
        print("Output ON with OVP set to 5.5V")

        print("Increasing voltage beyond OVP to trigger protection...")
        self.psu.setVoltage(channel, 6.0)
        time.sleep(2)

        status = self.psu.getOutStatus()
        print(f"Output status after OVP test: {status}")

        self.psu.clearOutput_Protection_Clear(channel)
        self.psu.setVoltage(channel, 5.0)
        self.psu.outp_ON(channel)
        print("Protection cleared, output restored")
        self.psu.outp_OFF(channel)
        print("=== OVP Protection Test Complete ===\n")

    def run_OCP_protection_test(self, channel=1):
        print("=== OCP Protection Test ===")
        self.psu.reset()
        self.psu.clear_errors()
        self.psu.setCurrent(channel, 1.0)
        self.psu.setOCP_Protection(channel, True)
        self.psu.setOCP_Delay(channel, 0.1)
        self.psu.outp_ON(channel)
        print("Output ON with OCP enabled at 1.0A")

        print("Increasing current beyond OCP to trigger protection...")
        self.psu.setCurrent(channel, 2.0)
        time.sleep(2)

        status = self.psu.getOutStatus()
        print(f"Output status after OCP test: {status}")

        self.psu.clearOutput_Protection_Clear(channel)
        self.psu.setCurrent(channel, 1.0)
        self.psu.outp_ON(channel)
        print("Protection cleared, output restored")
        self.psu.outp_OFF(channel)
        print("=== OCP Protection Test Complete ===\n")

    # --- Load and Line Regulation ---
    def run_load_regulation_test(self, channel=1):
        print("=== Load Regulation Test ===")
        self.psu.setVoltage(channel, 5.0)
        self.psu.setCurrent(channel, 0.5)
        self.psu.outp_ON(channel)
        time.sleep(1)

        regulation = self.psu.measure_load_regulation(channel, load_step=1.0)
        print(f"Load Regulation: {regulation:.3f} %")

        self.psu.outp_OFF(channel)
        print("=== Load Regulation Test Complete ===\n")

    def run_line_regulation_test(self, channel=1):
        print("=== Line Regulation Test ===")
        self.psu.setVoltage(channel, 5.0)
        self.psu.setCurrent(channel, 1.0)
        self.psu.outp_ON(channel)
        time.sleep(1)

        input("Please manually vary the line voltage and press Enter to continue...")

        regulation = self.psu.measure_line_regulation(channel, line_step=10)
        print(f"Line Regulation: {regulation:.3f} %")

        self.psu.outp_OFF(channel)
        print("=== Line Regulation Test Complete ===\n")

    # --- Burn-In / Stress Test ---
    def run_burn_in_test(self, channel=1, duration_sec=3600, voltage=5.0, current=1.0):
        print("=== Burn-In Stress Test ===")
        self.psu.setVoltage(channel, voltage)
        self.psu.setCurrent(channel, current)
        self.psu.outp_ON(channel)
        start_time = time.time()

        while time.time() - start_time < duration_sec:
            v = self.psu.measureVoltage(channel)
            i = self.psu.measureCurrent(channel)
            print(f"Time {time.time()-start_time:.1f}s: V={v:.3f} V, I={i:.3f} A")
            time.sleep(10)

        self.psu.outp_OFF(channel)
        print("=== Burn-In Stress Test Complete ===\n")

    # --- Transient Response Test ---
    def run_transient_response_test(self, channel=1):
        print("=== Transient Response Test ===")
        self.psu.reset()
        self.psu.clear_errors()
        self.psu.setVoltage(channel, 5.0)
        self.psu.setCurrent(channel, 1.0)
        self.psu.outp_ON(channel)

        self.psu.arb_select_voltage(channel)
        self.psu.arb_pulse_voltage(channel, v_start=5.0, v_top=7.0, t_start=0, t_top=0.01, t_end=0.05)
        self.psu.arb_set_last_value_on(channel)
        self.psu.arb_trigger()
        print("Transient pulse triggered")

        for i in range(5):
            v = self.psu.measureVoltage(channel)
            print(f"Voltage at t+{i*10}ms: {v:.3f} V")
            time.sleep(0.01)

        self.psu.outp_OFF(channel)
        print("=== Transient Response Test Complete ===\n")

    # --- Multi-Channel Tests ---
    def run_multi_channel_parallel_test(self, channels=[1, 2]):
        print("=== Multi-Channel Parallel Output Test ===")
        for ch in channels:
            self.psu.setVoltage(ch, 5.0)
            self.psu.setCurrent(ch, 2.0)
            self.psu.outp_ON(ch)
        time.sleep(2)

        voltages = [self.psu.measureVoltage(ch) for ch in channels]
        currents = [self.psu.measureCurrent(ch) for ch in channels]
        print(f"Voltages: {voltages}")
        print(f"Currents: {currents} (Sum: {sum(currents):.3f} A)")

        for ch in channels:
            self.psu.outp_OFF(ch)
        print("=== Multi-Channel Parallel Output Test Complete ===\n")

    def run_multi_channel_series_test(self, channels=[1, 2]):
        print("=== Multi-Channel Series Output Test ===")
        voltages_set = [3.3, 1.7]
        currents_set = [1.0, 1.0]
        for ch, v, i in zip(channels, voltages_set, currents_set):
            self.psu.setVoltage(ch, v)
            self.psu.setCurrent(ch, i)
            self.psu.outp_ON(ch)
        time.sleep(2)

        voltages = [self.psu.measureVoltage(ch) for ch in channels]
        currents = [self.psu.measureCurrent(ch) for ch in channels]
        print(f"Voltages: {voltages} (Sum: {sum(voltages):.3f} V)")
        print(f"Currents: {currents}")

        for ch in channels:
            self.psu.outp_OFF(ch)
        print("=== Multi-Channel Series Output Test Complete ===\n")

    # --- Sequencing Power-Up/Down ---
    def run_power_sequence(self, channels=[1, 2, 3], delay_sec=1.0):
        print("=== Multi-Channel Power-Up Sequence ===")
        for ch in channels:
            self.psu.setVoltage(ch, 3.3)
            self.psu.setCurrent(ch, 1.0)
            self.psu.outp_ON(ch)
            print(f"Channel {ch} ON")
            time.sleep(delay_sec)

        print("=== Multi-Channel Power-Down Sequence ===")
        for ch in reversed(channels):
            self.psu.outp_OFF(ch)
            print(f"Channel {ch} OFF")
            time.sleep(delay_sec)
        print("=== Power Sequence Complete ===\n")

    # --- Protection Trip and Recovery ---
    def run_protection_trip_recovery(self, channel=1):
        print("=== Protection Trip and Recovery Test ===")
        self.psu.reset()
        self.psu.clear_errors()

        self.psu.setOVP_Protection(channel, 4.0)
        self.psu.setOCP_Protection(channel, True)
        self.psu.setOCP_Delay(channel, 0.05)

        self.psu.setVoltage(channel, 3.3)
        self.psu.setCurrent(channel, 0.5)
        self.psu.outp_ON(channel)
        time.sleep(1)

        print("Triggering OVP trip by increasing voltage...")
        self.psu.setVoltage(channel, 5.0)
        time.sleep(1)
        print("Output status:", self.psu.getOutStatus())

        self.psu.clearOutput_Protection_Clear(channel)
        print("Protection cleared")

        print("Triggering OCP trip by increasing current...")
        self.psu.setCurrent(channel, 2.0)
        time.sleep(1)
        print("Output status:", self.psu.getOutStatus())

        self.psu.clearOutput_Protection_Clear(channel)
        print("Protection cleared")

        self.psu.outp_OFF(channel)
        print("=== Protection Trip and Recovery Test Complete ===\n")

    # --- Triggered Measurement ---
    def run_triggered_measurement(self, channel=1):
        print("=== Triggered Measurement Test ===")
        self.psu.my_instr.write(f'TRIG:SOUR EXT,(@{channel})')
        self.psu.outp_ON(channel)
        print("Waiting for external trigger...")

        time.sleep(5)  # Replace with event-driven wait in real system

        voltage = self.psu.measureVoltage(channel)
        current = self.psu.measureCurrent(channel)
        print(f"Triggered Measurement - Voltage: {voltage:.3f} V, Current: {current:.3f} A")

        self.psu.outp_OFF(channel)
        print("=== Triggered Measurement Test Complete ===\n")

    # --- Precision Characterization ---
    def run_precision_characterization(self, channel=1, voltage_points=None, current_limit=1.0):
        print("=== Precision Voltage-Current Characterization ===")
        if voltage_points is None:
            voltage_points = [0, 1, 2, 3, 4, 5]

        results = []
        for v in voltage_points:
            self.psu.setVoltage(channel, v)
            self.psu.setCurrent(channel, current_limit)
            self.psu.outp_ON(channel)
            time.sleep(0.5)
            measured_v = self.psu.measureVoltage(channel)
            measured_i = self.psu.measureCurrent(channel)
            print(f"Set V={v} V, Measured V={measured_v:.3f} V, Measured I={measured_i:.3f} A")
            results.append((v, measured_v, measured_i))
            self.psu.outp_OFF(channel)
            time.sleep(0.2)
        print("=== Characterization Complete ===")
        return results

    # --- Export Results to CSV ---
    def export_characterization_results_to_csv(self, results, filename="characterization_results.csv"):
        print(f"Exporting results to {filename}")
        with open(filename, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Set Voltage (V)", "Measured Voltage (V)", "Measured Current (A)"])
            for row in results:
                writer.writerow(row)
        print("Export complete.\n")

def main():
    # Initialize instrument control class (make sure you have N670x class defined and imported)
    from Instruments.n670x import N670x
    psu = N670x('USB0::0x2A8D::0x0F02::MY56002702::INSTR')
    ate = N670xATE(psu)

    try:
        ate.run_basic_functionality_test(channel=1)
        ate.run_OVP_protection_test(channel=1)
        ate.run_OCP_protection_test(channel=1)
        ate.run_load_regulation_test(channel=1)
        ate.run_line_regulation_test(channel=1)
        ate.run_burn_in_test(channel=1, duration_sec=300)  # 5-minute burn-in demo
        ate.run_transient_response_test(channel=1)
        ate.run_multi_channel_parallel_test(channels=[1, 2])
        ate.run_multi_channel_series_test(channels=[1, 2])
        ate.run_power_sequence(channels=[1, 2, 3])
        ate.run_protection_trip_recovery(channel=1)
        ate.run_triggered_measurement(channel=1)

        results = ate.run_precision_characterization(channel=1)
        ate.export_characterization_results_to_csv(results)

    finally:
        psu.close()
        print("Instrument connection closed.")

if __name__ == "__main__":
    main()
