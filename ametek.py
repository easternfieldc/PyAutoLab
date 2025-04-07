import pyvisa
import time

class SEQUOIA():
    OUTPUT_ON = "OUTP 1"
    OUTPUT_OFF = "OUTP 0"

    def __init__(self, ip: str):
        self.rm = pyvisa.ResourceManager()
        self.inst = self.rm.open_resource("TCPIP0::" + ip + "::INSTR")
        self.idn = self.query("*IDN?")
        if self.idn:
            print("Instrument ID: " + self.idn)
        else:
            print("Failed to connect to instrument.")
        self.write("VOLT:RANGE 333")
        self.phase = self.query("SYST:CONF:NOUT?")
        self.voltage = float(self.query("VOLT?"))
        self.frequency = float(self.query("FREQ?"))
        self.output = self.query("OUTP?")
        self.function = self.query("FUNC?")
        self.current_lim = float(self.query("CURR?"))
        self.set_current_limit(40)
        self.set_frequency(50.0)
        self.set_slew(1000)
        self.set_function()
        # self.set_voltage(0.0)

    def __del__(self):
        try:
            if hasattr(self, 'inst'):
                self.inst.close()
                print("Connection closed.")
        except Exception as e:
            print(f"Error closing connection: {e}")

    def query(self, msg: str):
        try:
            return self.inst.query(msg)
        except pyvisa.VisaIOError as e:
            print(f"Visa IO Error: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error: {e}")
            return None

    def write(self, msg: str):
        try:
            self.inst.write(msg)
        except pyvisa.VisaIOError as e:
            print(f"Visa IO Error: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")

    def set_current_limit(self, curr: float): # Arms
        self.write(f"CURR {curr}")
        _response = self.query("CURR?")
        if _response is not None:
            return float(_response)
        return None

    def set_slew(self, slew: float): # V/s
        self.write(f"VOLT:SLEW {slew}")
        _response = self.query("VOLT:SLEW?")
        if _response is not None:
            return float(_response)
        return None

    def set_voltage(self, volt: float):
        self.write(f"VOLT {volt}")
        _response = self.query("VOLT?")
        if _response is not None:
            self.voltage = float(_response)
        return self.voltage

    def set_frequency(self, freq: float):
        self.write(f"FREQ {freq}")
        _response = self.query("FREQ?")
        if _response is not None:
            self.frequency = float(_response)
        return self.frequency

    def set_volt_freq(self, volt: float, freq: float):
        self.voltage = self.set_voltage(volt)
        self.frequency = self.set_frequency(freq)
        return self.voltage, self.frequency
    
    def set_function(self, func: str = "SINE"):
        self.write("FUNC "+func)
        self.function = self.query("FUNC?")
        return self.function
    
    def select_phase(self, num: int = 3):
        self.write(f"SYST:CONF:NOUT {num}")
        self.phase = self.query("SYST:CONF:NOUT?")
        return self.phase

    def switch_output(self, on: bool, delay: float = 0.0):
        time.sleep(delay)
        if on:
            self.write(self.OUTPUT_ON)
            self.output = True
        else:
            self.write(self.OUTPUT_OFF)
            self.output = False
        return self.output
    
    def list(self, dwell: list, volt: list = [], freq: list = [], count: int = 1): # Test done
        if volt != []:
            self.write("VOLT:MODE LIST")
            print("Voltage list mode set.")
        if freq != []:
            self.write("FREQ:MODE LIST")
            print("Frequency list mode set.")
        _cmd = ""

        if volt != []:
            _cmd = "LIST:VOLT "
            for i in range(len(volt)):
                if i == 0:
                    _cmd = _cmd + str(volt[i])
                else:
                    _cmd = _cmd + ", " + str(volt[i])
            print(_cmd)
            self.write(_cmd)
        
        if freq != []:
            _cmd = "LIST:FREQ "
            for i in range(len(freq)):
                if i == 0:
                    _cmd = _cmd + str(freq[i])
                else:
                    _cmd = _cmd + ", " + str(freq[i])
            print(_cmd)
            self.write(_cmd)
        
        _cmd = "LIST:DWEL "
        for i in range(len(dwell)):
            if i == 0:
                _cmd = _cmd + str(dwell[i])
            else:
                _cmd = _cmd + ", " + str(dwell[i])
        print(_cmd)
        self.write(_cmd)

        self.write(f"LIST:COUN {count}") # How many times will you repeat the entire list
        self.write("LIST:STEP AUTO") # Not initiated step by step
        self.write("INIT") # Initiation trigger

if __name__ == "__main__":
    sq = SEQUOIA("192.168.0.30")
    print(sq.query("VOLT:RANGE?"))
    sq.write("SYST:CONF:NOUT 1") # Set single output phase
    sq.write("SYST:CONF:NOUT 3") # Set single output phase
    # sq.switch_output(True)
    # print(sq.set_volt_freq(20, 50))
    # sq.list([1, 1, 1], volt = [10, 20, 50])
    # sq.switch_output(False)