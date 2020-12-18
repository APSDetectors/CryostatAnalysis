# CryostatAnalysis
Python scripts to analyze and visualize HPD Model 107 ADR Cryostat log file data <br/>
<br/>
Works best with complete log files (from warmup to cooldown) <br/>
<br/>
cryostat_functions.py : Functions for loading, reformatting, and sorting log files, calculating summary quantities, and plotting log file data/summary quantities <br/>
GUI_107.py : Basic GUI for accessing functions in cryostat_functions.py. The GUI is divided into four quadrants with different functionalities, which are plots for a single phase (i.e. cooldown, warmup, one ADR cycle, one temperature hold), plots for multiple phases (i.e. all temperature holds in one log file), plots of summary quantities for multiple log files, and tables of summary quantities.
