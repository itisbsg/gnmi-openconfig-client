#
# ocWifi - Open Config Wifi Module
#
# services the get/set routes related wifi feature
#

import pyangbind.lib.pybindJSON as pybindJSON

from ocwifi_mac import *
from ocwifi_phy import *
from ocwifi_system import *

class ocWifi:
    """ processes requests regarding wifi feature """
    def __init__(self):
        pass

    @staticmethod
    def processGetMacRequest(arr):
        # FIXME: A lot to fix here
        ocwifiMac = openconfig_wifi_mac()
        ocwifiMac.ssids.ssid.add("hpn-byod")
        resp = pybindJSON.dumps(ocwifiMac.ssids.ssid, filter=False)
        return resp

    @staticmethod
    def processGetPhyRequest(arr):
        ocwifiPhy = openconfig_wifi_phy()
        resp = pybindJSON.dumps(ocwifiPhy, filter=False)
        return resp

    @staticmethod
    def processGetSystemRequest(arr):
        ocwifiSystem = openconfig_system_wifi_ext()
        resp = pybindJSON.dumps(ocwifiSystem, filter=False)
        return resp
