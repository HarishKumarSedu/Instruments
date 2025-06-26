from Instruments import A34461,N670x
import time 
# meter = A34461('USB0::0x2A8D::0x1401::MY57200246::INSTR')
if __name__ == "__main__":
    from Instruments.n67xx import N67xx
    ps = N67xx('USB0::0x0957::0x0F07::MY50002157::INSTR')
    ps.configure_current_sink_source(1)
    ps.set_current(1,current=-0.1)
    ps.output_state(state=True,chan=1)
    ps.configure_current_meter(3)
    print(ps.measure_current_dc(3))