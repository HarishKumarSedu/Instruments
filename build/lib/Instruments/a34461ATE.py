import time
import csv

class A34461ATE:
    """
    Complete ATE supported application for Keysight 34461A DMM.
    Integrates instrument control with automated test sequences, trigger detection,
    measurement averaging, error handling, and data export.
    """

    def __init__(self, dmm):
        """
        :param dmm: Instance of Keysight34461A instrument control class
        """
        self.dmm = dmm
        self.test_results = []

    def initialize_instrument(self):
        print("Initializing instrument...")
        self.dmm.initialize()
        print("Instrument initialized.")

    def run_basic_voltage_test(self, samples=5, delay=0.2):
        print("Running basic DC voltage test...")
        avg_voltage = self.dmm.measure_average('VOLT:DC', samples=samples, delay=delay)
        print(f"Average DC Voltage: {avg_voltage:.6f} V")
        self.test_results.append({'Test': 'Basic DC Voltage', 'Result': avg_voltage, 'Pass': True})
        return avg_voltage

    def run_resistance_test(self, samples=5, delay=0.2):
        print("Running resistance test...")
        self.dmm.configure_resistance()
        readings = []
        for _ in range(samples):
            self.dmm.initiate_measurement()
            time.sleep(delay)
            val = self.dmm.measure_resistance()
            readings.append(val)
        avg_resistance = sum(readings) / len(readings)
        print(f"Average Resistance: {avg_resistance:.3f} Ω")
        self.test_results.append({'Test': 'Resistance', 'Result': avg_resistance, 'Pass': True})
        return avg_resistance

    def run_capacitance_test(self, samples=5, delay=0.2):
        print("Running capacitance test...")
        self.dmm.configure_capacitance()
        readings = []
        for _ in range(samples):
            self.dmm.initiate_measurement()
            time.sleep(delay)
            val = self.dmm.measure_capacitance()
            readings.append(val)
        avg_capacitance = sum(readings) / len(readings)
        print(f"Average Capacitance: {avg_capacitance:.6e} F")
        self.test_results.append({'Test': 'Capacitance', 'Result': avg_capacitance, 'Pass': True})
        return avg_capacitance

    def wait_for_trigger_and_measure(self, func='VOLT:DC', timeout=10):
        print("Waiting for trigger event...")
        self.dmm.set_trigger_source('EXT')
        self.dmm.configure_function(func)
        self.dmm.set_trigger_count(1)
        self.dmm.initiate_measurement()

        start_time = time.time()
        while time.time() - start_time < timeout:
            if self.dmm.get_trigger_status():
                print("Trigger detected, measuring...")
                val = self.dmm.measure()
                print(f"Measurement after trigger: {val}")
                self.test_results.append({'Test': f'Triggered {func}', 'Result': val, 'Pass': True})
                return val
            time.sleep(0.1)
        print("Trigger timeout expired.")
        self.test_results.append({'Test': f'Triggered {func}', 'Result': None, 'Pass': False})
        return None

    def test_voltage_bandgap_trimming(self, trim_voltage_nominal=1.2, tolerance=0.01, samples=10):
        print("Starting Voltage Bandgap Trimming Test...")
        self.dmm.configure_voltage_dc()
        readings = []
        for _ in range(samples):
            self.dmm.initiate_measurement()
            time.sleep(0.05)
            v = self.dmm.measure_voltage_dc()
            readings.append(v)
        avg_v = sum(readings) / len(readings)
        print(f"Measured Bandgap Voltage: {avg_v:.4f} V")
        passed = abs(avg_v - trim_voltage_nominal) <= tolerance
        print(f"Bandgap Trim Test {'PASSED' if passed else 'FAILED'} (Tolerance ±{tolerance} V)")
        self.test_results.append({'Test': 'Voltage Bandgap Trimming', 'Result': avg_v, 'Pass': passed})
        return passed, avg_v

    def test_uvlo_detection(self, uvlo_threshold=3.3, samples=10, delay=0.1):
        print("Starting UVLO Detection Test...")
        self.dmm.configure_voltage_dc()
        readings = []
        for _ in range(samples):
            self.dmm.initiate_measurement()
            time.sleep(delay)
            v = self.dmm.measure_voltage_dc()
            readings.append(v)
        avg_v = sum(readings) / len(readings)
        print(f"Measured Voltage: {avg_v:.4f} V")
        uvlo_detected = avg_v < uvlo_threshold
        print(f"UVLO Detection {'DETECTED' if uvlo_detected else 'NOT DETECTED'} (Threshold {uvlo_threshold} V)")
        self.test_results.append({'Test': 'UVLO Detection', 'Result': avg_v, 'Pass': uvlo_detected})
        return uvlo_detected, avg_v

    def test_ocp_detection(self, ocp_current_threshold=1.0, samples=10, delay=0.1):
        print("Starting OCP Detection Test...")
        self.dmm.configure_current_dc()
        readings = []
        for _ in range(samples):
            self.dmm.initiate_measurement()
            time.sleep(delay)
            i = self.dmm.measure_current_dc()
            readings.append(i)
        avg_i = sum(readings) / len(readings)
        print(f"Measured Current: {avg_i:.4f} A")
        ocp_triggered = avg_i > ocp_current_threshold
        print(f"OCP Detection {'TRIGGERED' if ocp_triggered else 'NOT TRIGGERED'} (Threshold {ocp_current_threshold} A)")
        self.test_results.append({'Test': 'OCP Detection', 'Result': avg_i, 'Pass': ocp_triggered})
        return ocp_triggered, avg_i

    def export_results_to_csv(self, filename="ate_test_results.csv"):
        print(f"Exporting test results to {filename}...")
        with open(filename, mode='w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=['Test', 'Result', 'Pass'])
            writer.writeheader()
            for row in self.test_results:
                writer.writerow(row)
        print("Export complete.")

    def run_full_test_sequence(self):
        try:
            self.initialize_instrument()
            self.run_basic_voltage_test()
            self.run_resistance_test()
            self.run_capacitance_test()
            self.wait_for_trigger_and_measure(func='VOLT:DC')
            self.test_voltage_bandgap_trimming()
            self.test_uvlo_detection()
            self.test_ocp_detection()
            self.export_results_to_csv()
        except Exception as e:
            print(f"Error during test sequence: {e}")

    def initialize_instrument(self):
        print("Initializing instrument...")
        self.dmm.initialize()
        print("Instrument initialized.")
