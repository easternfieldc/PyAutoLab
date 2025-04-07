import pyvisa
import os

class WT5000:
    """
    Class to control WT5000 instrument via PyVISA.
    """

    def __init__(self, ip: str, verbose: bool = True):
        """
        Initialize connection to WT5000.

        Args:
            ip (str): IP address of the WT5000 instrument.
            verbose (bool): If True, prints debug information.
        """
        self.rm = pyvisa.ResourceManager()
        self.inst = self.rm.open_resource("TCPIP0::" + ip + "::INSTR")
        self.inst.timeout = 10000
        self.idn = self.inst.query("*IDN?")
        self.verbose = verbose
        if self.verbose:
            print("instrument ID: " + self.idn)

    def __del__(self):
        """
        Close the connection to the instrument.
        """
        if hasattr(self, 'inst'):
            self.inst.close()
            if self.verbose:
                print("Connection closed.")

    def query(self, msg: str):
        """
        Send a query message to the instrument and return the response.
        """
        return self.inst.query(msg)

    def write(self, msg: str):
        """
        Send a command to the instrument.
        """
        self.inst.write(msg)

    def remote(self, set: bool):
        """
        Enable or disable remote control of the instrument.

        Args:
            set (bool): True to enable remote control, False to disable.
        """
        _st = self.query("COMM:REM?")
        if self.verbose:
            print(f"Current remote state: {_st}")
        self.write(f"COMM:REM {'ON' if set else 'OFF'}")
        return self.query("COMM:REM?")

    def set_screen_name(self, name: str):
        """
        Set the name for saving the screen image.
        """
        if not name.isalnum():
            raise ValueError("Screen name must be alphanumeric.")
        self.write(f"IMAG:SAVE:NAME \"{name}\"")
        return self.query("IMAG:SAVE:NAME?")

    def set_screen_folder(self, folder: str, driv: str = "USER"):
        """
        Set the folder for saving the screen image.
        """
        self.set_screen_drive(driv)
        self.write(f"IMAG:SAVE:CDIR \"{folder}\"")
        return self.query("FILE:PATH?")

    def set_screen_drive(self, driv: str):
        """
        Set the drive for saving the screen image.
        """
        if driv not in ["USER", "USB", "NETW", "NETWork"]:
            raise ValueError(f"Invalid drive: {driv}. Must be 'USER', 'USB', or 'NETWork'.")
        self.write(f"IMAG:SAVE:DRIV {driv}")

    def save_screen(self):
        """
        Save the current screen image to the configured location.
        """
        self.write("IMAG:EXEC")

if __name__ == "__main__":
    wt = WT5000("192.168.0.5")
    # print(wt.query("FILE:PATH?"))
    # wt.set_screen_folder("LDC")
    # wt.set_screen_folder("OBC")
    # wt.set_screen_name("TEST001")
    # wt.save_screen()
    wt.write("IMAG:FORM PNG")
    wt.write("IMAG:SEND?")
    ret = wt.inst.read()
    print(ret)