# Mininet-Project

## dumbbel_topo.py
Mininet Python API implementation to build the dumbbell topology. This script defines the network topology with hosts and switches connected in a dumbbell structure.

## tcp_workload.py
Runs TCP workload simulations on the Mininet Dumbbell Topology. It sets up TCP connections between hosts and measures performance metrics like throughput and latency.

## trace_tcp_perf.py
Executes the Mininet workload and traces system performance using `iperf3`. Outputs include a data file, a human-readable report, and graphs generated using Matplotlib.

## Usage
The mininet-vm image running Ubuntu Focal (20.04) was used for the following operations. 
Development was conduted with the aid of VSCode SSH.
### Dependencies & Environment
It is reccomended to create a python virtualenv and install the needed packages from `requirements.txt`
Use apt-get to install the below packages (virtualenv, perf)
* python3-venv
* linux-tools-$(uname -r)
* iperf3
```
sudo apt update && sudo apt instal -y --no-install-recommends python3-venv linux-tools-$(uname -r) iperf3
```
***
Then in the root of this project, run:
```
$ python3 -m venv myvenv
$ source myvenv/bin/activate
(myvenv)$ python -m pip install -r requirements.txt
```
### Running Experiments
Refer to the [spreadsheet][def] for all the combinations of experiments. Simply copy and paste them into your terminal. 
> **NOTE:** This assumes you are within your Python Virtual Environment!

For example, run the very first experiment with:
```
sudo $(pwd)/myvenv/bin/python3 trace_tcp_perf.py --experiment exp1 --delay 21 --cctrl reno
```
[def]: Sorted_TCP_Experiment_Commands.csv