# Mininet-Project

## dumbbel_topo.py
Mininet Python API implementation to build the dumbbell topology as shown in the assignment description

## tcp_reno.py
Runs TCP RENO Congestion Control with Mininet

## trace_tcp_perf.py
Runs the Mininet workload and Perf tracing in two seperate threads. Perf then outputs the data file and calls the "report" method to produce a human readable output. Matplotlib used to generate graphs.

## Running
The mininet-vm image running Ubuntu Focal (20.04) was used for the following operations. 
Development was conduted with the aid of VSCode SSH.
### Pre-requisite
It is reccomended to create a python virtualenv and install the needed packages from `requirements.txt`
Use apt-get to install the below packages (virtualenv, perf)
* python3-venv
* linux-tools-$(uname -r)
***
Once the __perf__ tool has been installed,
enable the system __tcp_probe__ kernel tracepoint:
```
sudo -i
cd /sys/kernel/tracing
echo 1 > events/tcp/tcp_probe/enable
```
There was a warning when running the perf on the terminal

`Cannot load tips.txt file, please install perf!`

To solve this warning: 
copy tips.txt from https://github.com/torvalds/linux/blob/master/tools/perf/Documentation/tips.txt to *__/usr/share/doc/perf-tip/tips.txt__*
***
Then in the root of this project, run:
```
$ python3 -m venv myvenv
$ source myvenv/bin/activate
(myvenv)$ python -m pip install -r requirements.txt

```
### Recording Trace
The Python script __trace_tcp_perf.py__ automates the process of starting mininet (TCP RENO) in the dumbbell topology, running "perf record", generating the perf script, parsing the script for "snd_cwnd", & generating plots with matplotlib. It needs to run as sudo. To avoid "Module Not Found errors", activate the python virtualenv and run like so:
```
(myvenv)$ sudo /home/mininet/Mininet-Project/myvenv/bin/python trace_tcp_perf.py
```