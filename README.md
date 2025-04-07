# PyAutoLab
A Python library for lab automation.

## Compatibility
This library is written and validated for following instruments:
1. AMETEK SQUOIA SQ0030C1G1 - Bidirectional AC Power Supply
1. Chroma 62120D-1200 - Bidirectional DC Power Supply
1. YOKOGAWA WT5000 - Power Analyzer
1. Teledyne LeCroy WaveRunner8100HD - Oscilloscope

Also PyAuto shall be compatible with the instruments that share the same [SCPI](https://www.ivifoundation.org/About-IVI/scpi.html) command.

## How to use
It is strongly recommended that you use an [anaconda](https://www.anaconda.com/) or a [miniconda](https://www.anaconda.com/docs/getting-started/miniconda/main) environment.

Download anaconda or miniconda from the website and install it.
Create an environment with the command below
`conda create -n <your_env_name> python=<your_python_version>`
For example, `conda create -n pyauto python=3.11`

Install following packages using `pip install <package_name>`
- [pyvisa](https://pyvisa.readthedocs.io/en/latest/)
- [pywin32](https://timgolden.me.uk/pywin32-docs/contents.html)
- (Optional) [numpy](https://numpy.org/)
- (Optional) [pandas](https://pandas.pydata.org/)

Each class is in the file named after its manufacturer. Import the class you want.
```
from lecroy_dso import WaveRunner
from chroma import BiDCPower
from ametek import SEQUOIA
from yokogawa import WT5000
```

Initialize the class as an object
```
osc = WaveRunner("192.168.xxx.xxx")
dcp = BiDCPower("192.168.xxx.xxx")
acp = SEQUOIA("192.168.xxx.xxx")
poa = WT5000("192.168.xxx.xxx")
```

And enjoy!
