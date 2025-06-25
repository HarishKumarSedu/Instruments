from Instruments import A34461
import time 
# meter = A34461('USB0::0x2A8D::0x1401::MY57200246::INSTR')
if __name__ == "__main__":
    resource = "USB0::0x2A8D::0x1401::MY57200246::INSTR"
    dmm = A34461(resource)
    # Configure DC voltage with 10 V range and 50 uV resolution 1NPLC
    dmm.configure_voltmeter(10, resolution=50e-6,autozero='ON',impedance='AUTO')
    dmm.set_sample_count(1)
    dmm.set_trigger_source('IMM')
    dmm.set_trigger_delay(0)
    # time.sleep(1)
    print(dmm.measure())


    dmm.close()
