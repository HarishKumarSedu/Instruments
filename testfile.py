from Instruments import A34461,N670x
import time 
# meter = A34461('USB0::0x2A8D::0x1401::MY57200246::INSTR')
if __name__ == "__main__":
    import pyvisa as visa
    print(visa.ResourceManager().list_resources())