

# Report on Trigger Setup and Measurement Methods Using Tektronix DPO4054

## Introduction

This report explains how to configure trigger settings and perform frequency measurements on the Tektronix DPO4054 oscilloscope using Python. It highlights two measurement approaches:

- **Immediate Measurement:** Measurement requested and returned immediately.
- **Normal Slot Measurement:** Measurement assigned to a slot on the oscilloscope and retrieved later.

The sample code demonstrates these concepts and the workflow for data acquisition.

---

## Sample Code

```python
from Instruments import DPO4054
from time import sleep

# Initialize the oscilloscope with USB resource string
osc = DPO4054('USB0::0x0699::0x0401::C020132::INSTR')

# Disable display on channel 1
osc.set_channel_display(channel=1, display=False)

# Set timebase scale to half the input signal frequency (125 Hz)
osc.set_timebase_scale(1 / (2 * 125))  # Input signal frequency: 125 Hz

# Configure channel 3:
# Label as 'clk', enable display, 1 V/div scale, 0 position, 0 offset,
# DC coupling, full bandwidth, no inversion
osc.setup_channel(
    channel=3,
    label='clk',
    display=True,
    scale=1,
    position=0.0,
    offset=0.0,
    coupling='DC',
    bandwidth='FULL',
    invert=False
)

# Setup trigger on channel 3:
# Level set to 90% of 1.8 V digital signal, rising edge, edge trigger mode
osc.trigger_setup(channel=3, level=1.8 * 0.9, slope='RISE', mode='EDGE')

# Add immediate frequency measurement on channel 3
osc.add_immediate_measurement(channel=3, meas_type='FREQ', source=1)

# Start single acquisition sequence with 20 s timeout and 1 µs sampling interval
osc.single_sequence(timeout=20, sampling_interval=1e-6)

# Wait 1 second for acquisition to complete
sleep(1)

# Retrieve and print immediate frequency measurement
print(f'FREQ immediate : {osc.get_immediate_measurement()}')

# Uncomment below to use normal slot measurement instead:
# osc.add_measurement(channel=3, meas_type='FREQ', slot=1, source=1)
# print(f'FREQ : {osc.get_measurement(channel=3, slot=1, source=1)}')

# Return oscilloscope to continuous acquisition mode
osc.set_continuous_acquisition()

# Close the instrument connection
osc.close()
```


---

## Explanation of Measurement Approaches

### Immediate Measurement

- **What it is:**
A measurement performed on-demand and returned immediately without pre-assigning a measurement slot.
- **In the code:**

```python
osc.add_immediate_measurement(channel=3, meas_type='FREQ', source=1)
...
print(f'FREQ immediate : {osc.get_immediate_measurement()}')
```

- **Use case:**
Quick checks or single-shot measurements where you want the latest value without managing measurement slots.
- **Pros:**
    - Simple and fast.
    - No need to manage measurement slots.
    - Flexible for scripting.
- **Cons:**
    - May not be optimal for multiple simultaneous measurements.

---

### Normal Slot Measurement

- **What it is:**
Measurement assigned to a numbered slot on the oscilloscope, continuously updated and queried as needed.
- **In the code (commented out):**

```python
# osc.add_measurement(channel=3, meas_type='FREQ', slot=1, source=1)
# print(f'FREQ : {osc.get_measurement(channel=3, slot=1, source=1)}')
```

- **Use case:**
Automated test setups requiring multiple measurements tracked simultaneously.
- **Pros:**
    - Efficient for repeated or multiple measurements.
    - Allows concurrent measurement management.
- **Cons:**
    - Requires upfront configuration and slot management.

---

## Workflow Summary

1. **Initialize** the oscilloscope connection.
2. **Configure channels** and **timebase**.
3. **Set trigger** parameters (channel, level, slope, mode).
4. **Add measurement** (immediate or slot-based).
5. **Acquire data** (single sequence or continuous).
6. **Retrieve measurement** results.
7. **Return to continuous acquisition** if needed.
8. **Close** the instrument connection.

---

## Conclusion

The sample code effectively demonstrates how to set up trigger and channel parameters, perform frequency measurements, and manage acquisition modes on the Tektronix DPO4054. Immediate measurements offer a quick and flexible way to get measurement data, while normal slot measurements provide a structured approach for complex testing scenarios.


