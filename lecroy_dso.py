import win32com.client
import os.path
import json
import pandas as pd
import numpy as np

class WaveRunner():
    def __init__(self, ip: str):
        try:
            self.inst = win32com.client.Dispatch("LeCroy.ActiveDSOCtrl.1")
        except Exception as e:
            print(f"Error initializing ActiveDSO: {e}")

        if not self.inst.MakeConnection("IP:"+ip):
            raise Exception(f"Failed to connect to oscilloscope at IP: {ip}")
        
        self.set_screen()

    def __del__(self):
        try:
            self.inst.Disconnect()
        except Exception as e:
            print(f"Error closing connection: {e}")
        
    def write(self, msg: str):
        """
        Sends a message and returns the ActiveDSO return value.
        """
        return self.inst.WriteString(msg, True)
        
    def query(self, msg: str):
        """
        Sends a message and returns the query.
        """
        self.write(msg)
        _ret = self.inst.ReadString(80)
        return _ret
    
    def set_screen(self):
        """
        Initializes the current screen format before screen dump is requested.
        """
        _cmd = "HCSU DEV, PNG, FORMAT, LANDSCAPE, BCKG, BLACK, AREA, FULLSCEEN, PORT, NET"
        if not self.write(_cmd):
            print("Failed to set Screendump")
        else:
            pass

    def save_screen_old(self, path: str, name: str):
        try:
            self.write("SCDP")
            _dump = self.inst.ReadBinary(204800)
            _dst_path = os.path.join(path, name)
            if ".png" not in name:
                _dst_path += ".png"
            with open(_dst_path, "wb+") as f:
                f.write(_dump)
        except Exception as e:
            print(f"Screen Dump Failed: {e}")

    def save_screen(self, path: str, name: str):
        _dst_path = os.path.join(path, name)
        if ".png" not in name:
            _dst_path += ".png"
        try:
            self.inst.StoreHardcopyToFile("PNG", "", _dst_path)
        except Exception as e:
            print(f"Screen Dump Failed: {e}")

    def get_panel(self, print_out: bool = False):
        _panel_string = self.inst.GetPanel()
        if print_out:
            print(_panel_string)
        return _panel_string
    
    def set_panel(self, buffer: str):
        return self.inst.SetPanel(buffer)
    
    def save_panel_to_file(self, path: str, name: str):
        _dst_path = os.path.join(path, name)
        if ".json" not in name:
            _dst_path += ".json"
        try:
            _panel_data = self.get_panel()
            with open(_dst_path, "w", encoding="utf-8") as json_file:
                json.dump({"panel": _panel_data}, json_file, ensure_ascii=False, indent=4)
            print(f"Panel data saved to {_dst_path}")
        except Exception as e:
            print(f"Failed to save panel data: {e}")

    def load_panel_from_file(self, path: str, name: str):
        _dst_path = os.path.join(path, name)
        if ".json" not in name:
            _dst_path += ".json"
        if not os.path.exists(_dst_path):
            raise FileNotFoundError(f"File not found: {_dst_path}")
        try:
            with open(_dst_path, "r", encoding="utf-8") as json_file:
                _data = json.load(json_file)
            _panel_data = _data.get("panel", "")
            if _panel_data:
                self.set_panel(_panel_data)
                print(f"Panel data loaded from {_dst_path}")
            else:
                print("No valid panel data found in JSON file.")
        except Exception as e:
            print(f"Failed to load panel data: {e}")

    def recall_panel(self, drive: str, path: str):
        """
        recalls panel setup from the oscilloscope
        """
        self.write(f"RCPN DISK,{drive},FILE,'{path}'")

    def set_trigger_mode(self, mode: str = "AUTO"):
        self.write("TRMD "+mode)
        _ret = self.query("TRMD?")
        print(_ret)
        return _ret
    
    def set_trigger_level(self, level, chan: str = ""):
        _cmd = chan+":TRIG_LEVEL "+str(level)
        self.write(_cmd)
        _ret = self.query(chan+":TRIG_LEVEL?")
        return _ret

    def set_timebase(self, t, unit: str = "S"):
        _unit = unit.upper()
        _valid_units = ["S", "MS", "US", "NS"]
        if _unit not in _valid_units:
            raise ValueError(f"Invalid timebase unit: {_unit}. Valid options are {_valid_units}.")
        _cmd = f"TIME_DIV {t}"+_unit
        self.write(_cmd)
        _ret = self.query("TIME_DIV?")
        return _ret
    
    def get_time_series_data(self, chan: str = "C1", len: int = 5000000): # len = 5000000 for 20 seconds
        """
        Gets a waveform with its corresponding time on the current screen.
        """
        _waveform = np.array(self.inst.GetScaledWaveformWithTimes(chan, len, 0))
        _waveform = np.transpose(_waveform)
        return pd.DataFrame(_waveform, index=["time", chan])
    
    def save_data(self, data: pd.DataFrame, path: str, name: str):
        _dst_path = os.path.join(path, name)
        if ".dat" not in name:
            _dst_path += ".dat"
        try:
            data.to_csv(_dst_path, index=False)
            print(f"Panel data saved to {_dst_path}")
        except Exception as e:
            print(f"Failed to save panel data: {e}")
    

if __name__ == "__main__":
    import time
    osc = WaveRunner("169.254.164.246")
    # print(osc.query("*IDN?"))
    # osc.set_trigger_mode("NORMAL")
    # osc.set_trigger_mode("AUTO")
    # time.sleep(25)
    osc.save_screen("D:\\My Documents\\Python\\pyauto\\screenshot", "FRS2-4_1P_TC45_2.png")
    # osc.save_screen("D:\\My Documents\\Python\\pyauto\\screenshot", "FRS2-4_1P_TC171_F.png")
    # osc.save_panel_to_file("panel", "CEER_TC171.json")
    # osc.load_panel_from_file("panel", "INITIAL_DEVICE_OPERATION.json")
    # time.sleep(10)
    # osc.load_panel_from_file("panel", "osc_panel_data_simple.json")
    # osc.set_trigger_level(310, "C1")
    # osc.set_trigger_mode("SINGLE")
    # osc.set_timebase(10, "S")


    # ret = osc.inst.GetNativeWaveform("C6", 5000, True, "ALL")
    # print(type(ret))
    # print(ret)
    # print(ret.tobytes())
    # for d in ret:
    #     print(d)