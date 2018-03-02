#
# ocShim.py
#
# Open Config Shim
#

from ocWifi import ocWifi

class ocShim:
    """ Open Config Shim Layer that mux/demuxes requests to/from other openconfig feature modules """
    def __init__(self):
        pass

    @staticmethod
    def processGetRequest(arr):
        if len(arr) < 2:
            print "Invalid request"
            return None

        if arr[0] == "wifi" and arr[1] == "mac":
            resp = ocWifi.processGetMacRequest(arr[2:])
        elif arr[0] == "wifi" and arr[1] == "phy":
            resp = ocWifi.processGetPhyRequest(arr[2:])
        elif arr[0] == "wifi" and arr[1] == "system":
            resp = ocWifi.processGetSystemRequest(arr[2:])
        else:
            resp = "Invalid Path..."
        return resp

    @staticmethod
    def processSubscribeRequest(arr):
        return ocShim.processGetRequest(arr)

