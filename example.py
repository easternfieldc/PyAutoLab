from lecroy_dso import WaveRunner
from chroma import BiDCPower
from ametek import SEQUOIA
from yokogawa import WT5000
import time

if __name__ == "__main__":
    osc = WaveRunner("192.168.0.10")
    dcp = BiDCPower("192.168.0.35")
    acp = SEQUOIA("192.168.0.30")
    poa = WT5000("192.168.0.5")

    osc.load_panel_from_file("panel", "osc_panel_data_detailed.json")
    osc.set_timebase(2)
    osc.set_trigger_mode("AUTO")
    time.sleep(1)
    osc.set_trigger_mode("NORMAL")
    time.sleep(1)
    osc.set_trigger_level(310, "C1")
    osc.set_trigger_mode("SINGLE")
    dcp.set_voltage(0)
    time.sleep(1)
    dcp.switch_output(True)
    dcp.set_voltage(290)
    time.sleep(5)
    dcp.set_slew(0.004)
    dcp.set_voltage(330)
    time.sleep(15)
    osc.save_screen("screenshot", "test_data.png")
    waveform = osc.get_time_series_data("C1", 5000000)
    osc.save_data(waveform, "data", "test_data")
    dcp.switch_output(False)

    import seaborn as sns
    import matplotlib.pyplot as plt

    sns.set_style('whitegrid')
    sns.lineplot(x=waveform[0], y=waveform[1])
    plt.show()