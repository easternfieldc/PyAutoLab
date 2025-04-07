import pyvisa
import time

### Bidirectional DC Power Supply 62120D-1200 ###
class BiDCPower():
    def __init__(self, ip: str):
        self.rm = pyvisa.ResourceManager()
        self.inst = self.rm.open_resource("TCPIP0::" + ip + "::INSTR")
        self.idn = self.query("*IDN?")
        if self.idn:
            print("Instrument ID: " + self.idn)
        else:
            print("Failed to connect to instrument.")
        self.output = False
        self.mode = "Source-Load"
        self.voltage = float(self.query("SOUR:VOLT?"))  # [V]
        self.slew = float(self.query("SOUR:VOLT:SLEW?"))  # [V/ms]
        self.source_current_lim = float(self.query("SOUR:CURR:LIM:LOW?"))
        self.load_current_lim = float(self.query("LOAD:CURR:PROT:HIGH?"))
        self.set_slew(1.0)
        # print(self.query("SOUR:CURR:PROT:HIGH?"))
        # print(self.query("SOUR:CURR:LIM:HIGH?"))
        # print(self.query("SOUR:CURR:LIM:LOW?"))
        self.set_source_current_limit(40)
        self.set_load_current_limit(40)
        print("Current Bi-directional DC Power Mode: " + self.mode)

    def __del__(self):
        try:
            if hasattr(self, 'inst'):
                self.inst.close()
                print("Connection closed.")
        except Exception as e:
            print(f"Error closing connection: {e}")

    def query(self, msg: str):
        return self.inst.query(msg)

    def write(self, msg: str):
        self.inst.write(msg)

    def switch_output(self, on: bool):
        if on:
            self.write("OUTP ON")
            self.output = True
        else:
            self.write("OUTP OFF")
            self.output = False
        return self.output

    def set_mode(self, _mode: str = "SOURCE-LOAD"):  # SOURCE-LOAD | SOUR | LOAD
        self.write("SYST:MODE " + _mode)
        self.mode = self.query("SYST:MODE?")
        return self.mode

    def set_voltage(self, volt: float):
        try:
            _max_volt = float(self.query("SOUR:VOLT? MAX"))
            _min_volt = float(self.query("SOUR:VOLT? MIN"))
        except ValueError:
            print("Error reading voltage range from device.")
            return None

        if volt >= _max_volt:
            self.write("SOUR:VOLT MAX")
        elif volt <= _min_volt:
            self.write("SOUR:VOLT MIN")
        else:
            self.write(f"SOUR:VOLT {volt}")
        
        self.voltage = float(self.query("SOUR:VOLT?"))
        return self.voltage

    def set_slew(self, _slew: float):
        try:
            max_slew = float(self.query("SOUR:VOLT:SLEW? MAX"))
            min_slew = float(self.query("SOUR:VOLT:SLEW? MIN"))
        except ValueError:
            print("Error reading slew rate range from device.")
            return None

        if _slew >= max_slew:
            self.write("SOUR:VOLT:SLEW MAX")
        elif _slew <= min_slew:
            self.write("SOUR:VOLT:SLEW MIN")
        else:
            self.write(f"SOUR:VOLT:SLEW {_slew}")
        
        self.slew = float(self.query("SOUR:VOLT:SLEW?"))
        return self.slew

    def set_source_current_limit(self, curr: float):
        self.write("SOUR:CURR:PROT:HIGH MAX")
        self.write("SOUR:CURR:LIM:HIGH MAX")
        try:
            _max_curr = float(self.query("SOUR:CURR:LIM:LOW? MAX"))
            _min_curr = float(self.query("SOUR:CURR:LIM:LOW? MIN"))
        except ValueError:
            print("Error reading voltage range from device.")
            return None

        if curr >= _max_curr:
            self.write("SOUR:CURR:LIM:LOW MAX")
        elif curr <= _min_curr:
            self.write("SOUR:CURR:LIM:LOW MIN")
        else:
            self.write(f"SOUR:CURR:LIM:LOW {curr}")
        
        self.source_current_lim = float(self.query("SOUR:CURR:LIM:LOW?"))
        return self.source_current_lim

    def set_load_current_limit(self, curr: float):
        try:
            _max_curr = float(self.query("LOAD:CURR:PROT:HIGH? MAX"))
            _min_curr = float(self.query("LOAD:CURR:PROT:HIGH? MIN"))
        except ValueError:
            print("Error reading voltage range from device.")
            return None

        if curr >= _max_curr:
            self.write("LOAD:CURR:PROT:HIGH MAX")
        elif curr <= _min_curr:
            self.write("LOAD:CURR:PROT:HIGH MIN")
        else:
            self.write(f"LOAD:CURR:PROT:HIGH {curr}")
        
        self.load_current_lim = float(self.query("LOAD:CURR:PROT:HIGH?"))
        return self.load_current_lim

### Regenerative Grid Simulator 61815 ###
class GridSimulator():
    OUTPUT_ON = "OUTP ON"
    OUTPUT_OFF = "OUTP OFF"

    def __init__(self, ip: str):
        self.rm = pyvisa.ResourceManager()
        self.inst = self.rm.open_resource("TCPIP0::" + ip + "::INSTR")
        self.idn = self.query("*IDN?")
        print(self.query("SYST:ERR?"))
        if self.idn:
            print("Instrument ID: " + self.idn)
        else:
            print("Failed to connect to instrument.")
        self.voltage = float(self.query("VOLT:AC?"))
        self.frequency = float(self.query("FREQ?"))
        self.output = self.query("OUTP?")
        self.set_slew(1.0)

    def __del__(self):
        try:
            if hasattr(self, 'inst'):
                self.inst.close()
                print("Connection closed.")
        except Exception as e:
            print(f"Error closing connection: {e}")

    def query(self, msg: str):
        return self.inst.query(msg)

    def write(self, msg: str):
        self.inst.write(msg)

    def set_voltage(self, volt: float):
        _max_volt = 350.0    # from manual
        _min_volt = 0.0      # from manual

        if volt >= _max_volt:
            self.write("VOLT:AC 350")
        elif volt <= _min_volt:
            self.write("VOLT:AC 0")
        else:
            self.write(f"VOLT:AC {volt}")
        
        self.voltage = float(self.query("VOLT:AC?"))
        return self.voltage

    def set_slew(self, slew: float): # V/ms
        self.write(f"OUTP:SLEW:VOLT:AC {slew}")
        _response = self.query("OUTP:SLEW:VOLT:AC?")
        if _response is not None:
            return float(_response)
        return None

    def set_frequency(self, freq: float):
        _max_freq = 100.0    # from manual
        _min_freq = 30.0     # from manual

        if freq >= _max_freq:
            self.write("FREQ 100")
        elif freq <= _min_freq:
            self.write("FREQ 30")
        else:
            self.write(f"FREQ {freq}")
        
        self.frequency = float(self.query("FREQ?"))
        return self.frequency

    def switch_output(self, on: bool, delay: float = 0.0):
        time.sleep(delay)
        if on:
            self.write(self.OUTPUT_ON)
            self.output = True
        else:
            self.write(self.OUTPUT_OFF)
            self.output = False
        return self.output


if __name__ == "__main__":
    chroma = BiDCPower("192.168.0.35")
    # chroma.set_mode("SOUR")
    # print(float(chroma.set_slew(1)))
    # print(float(chroma.query("SOUR:VOLT:SLEW? MIN")))
    # print(float(chroma.query("SOUR:VOLT:SLEW?")))