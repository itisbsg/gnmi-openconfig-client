# gnmi-openconfig-client
Python implementation of GNMI Client with REPL shell interface. Should work with any gnmi target. Implements gnmi rpcs such as capabilities, get, subscribe with easily cli interface. There are 3 components to this gnmi-client, gnmi-openconfig protos/yang model files, gnmi-target. gnmi-target is a dummy server and should be replaced with a real gnmi-target.

## Pre-Requisites
* Requires the following python packages, cmd2, pyang, pybindplugin
```
pip install cmd2
pip install pyang
```
* Pybindpugin is at https://github.com/robshakir/pyangbind
* Copy gnmi.proto file from github
```
git clone https://github.com/openconfig/gnmi/tree/master/proto
```
* Generate python classes for gnmi.proto. Check out grpc.io
* Expects the openconfig yang models are in local directory (under public)
```
git clone https://github.com/openconfig/public.git
```
* Use pyang and pybindplugin to build python classes from yang model files
```
pyang --plugindir $PYBINDPLUGIN -f pybind -p public/release/models/ -o ocwifi_mac.py public/release/models/wifi/mac/openconfig-wifi-mac.yang
```
* To enable cert based gnmi authentication with the server, create self-signed certs
```
openssl req -x509 -sha256 -nodes -days 365 -newkey rsa:2048 -keyout privateKey.key -out certificate.crt
openssl x509 -in certificate.crt -text -noout
```

## Running the client & server
The following sections explain how-to & options available to run client and targets

### starting a gnmi server
gNMITarget is a dummy gnmi server which uses the gnmi interface to connect to any gnmi client and implements a minimal rpc commands (so far capabilities andget).

* With TLS
```
$ python2.7 gNMITarget.py --tls -cert certs/certificate.crt -pvtkey certs/private.key localhost:5001
```

* Without TLS
```
$ python2.7 gNMITarget.py localhost:5001
```

### starting a gnmi client repl
gNMI Client has a REPL interactive interface and all commands have help online (help <cmd>). So far you can do
the following
* describe open config modles (describe)
* connect to a gNMI Target/Server (both clear or TLS certs based) (connect)
* issue commands such as capabilities, get (capabilities, get)
* TODO: set and subscribe

```

$ python2.7 gNMIClient.py
Welcome to the GNMI Client CLI. Type help or ? to list commands

ocREPL# ?

Documented commands (type help <topic>):
========================================
capabilities  connect  describe  get  help  history  quit  set  shortcuts

ocREPL#
```
## Screenshots
![Screenshort]screenshot.gif
