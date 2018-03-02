#
# GNMI Client
#

import os
import argparse
from cmd2 import Cmd, options, with_argparser, with_argument_list

import grpc

import gnmi_pb2
import gnmi_pb2_grpc

from gNMIUtils import gNMIUtils

#
# class gNMIClient
#
class gNMIClient:
    """gNMIClient is a wrapper for client side of gnmi proto spec"""

    def __init__(self, targetUrl, tlsEnabled, caCertPath, clientCertPath, privKeyPath):
        self.targetUrl = targetUrl
        if tlsEnabled == True:
            # secure grpc connection
            with open(caCertPath) as f:
                trustedCerts = f.read()
            credentials = grpc.ssl_channel_credentials(trustedCerts, None, None)
            self.__grpcChannel = grpc.secure_channel(targetUrl, credentials)
        else:
            # insecure grpc connection
            self.__grpcChannel = grpc.insecure_channel(targetUrl)

        self.__grpcStub = gnmi_pb2_grpc.gNMIStub(self.__grpcChannel)

    def __getGetRequestObj(self, path):
        # Check the validity of the Path
        if len(path) == 0 or path[0] != '/':
            return None

        # Create getReq object
        getReq = gnmi_pb2.GetRequest()
        getReq.type = gnmi_pb2.GetRequest.CONFIG
        getReq.encoding = gnmi_pb2.JSON

        # Parse the Path and fill the getReq object
        tokens = path[1:].split('/')
        if gNMIUtils.fillPrefix(tokens, getReq.prefix) is False \
           or \
           gNMIUtils.fillPath(tokens[len(tokens)-1], getReq.path.add()) is False:
               return None

        return getReq

    def __getSubscribeRequestObj(self, path):
        if len(path) == 0 or path[0] != '/':
            yield None

        tokens = path[1:].split('/')

        # SubscribeList
        sublist = gnmi_pb2.SubscriptionList()
        gNMIUtils.fillPrefix(tokens, sublist.prefix) # Prefix

        # Add subscription
        mysub = sublist.subscription.add()
        gNMIUtils.fillPath(tokens[len(tokens)-1], mysub.path) # Path
        mysub.mode = 0 # Mode = TARGET_DEFINED
        mysub.sample_interval = 0
        mysub.suppress_redundant = 0
        mysub.heartbeat_interval = 0

        # Model data
        modelData = sublist.use_models.add()
        modelData.name = "my_model"
        modelData.organization = "My Company Inc"
        modelData.version = "1.0"

        sublist.mode = 0 # Stream
        sublist.allow_aggregation = False
        sublist.encoding = 0 # JSON
        sublist.updates_only = False


        # Create a subscribe request
        subReq = gnmi_pb2.SubscribeRequest(subscribe = sublist)

        #print subReq

        yield subReq


    # gNMI Capability Request
    def capabilitiesRequest(self):
    	return self.__grpcStub.Capabilities(gnmi_pb2.CapabilityRequest())

    # gNMI GET Request
    def getRequest(self, e):
        req = self.__getGetRequestObj(e)
        if req is None:
            print "Path \"%s\" is invalid or invalid formate" % (e)
            return None
    	resp = self.__grpcStub.Get(req)
    	return resp

    def setRequest(request):
    	resp = self.__grpcStub.Set(request)
    	return resp

    def subscribeRequest(self, path):
        req = self.__getSubscribeRequestObj(path)
        if req is None:
            print "Something is wrong !!"
            return None
        resp = self.__grpcStub.Subscribe(req)
        try:
            for r in resp:
                print r
        except KeyboardInterrupt:
            print "Stopped by user input"



#
# class gNMIClientCli
#
class gNMIClientCli (Cmd):
    """docstring for gNMIClientCli"""
    intro = "Welcome to the GNMI Client CLI. Type help or ? to list commands \n"
    prompt = 'ocREPL# '

    #def __init__(self, targetUrl, tlsEnabled, caCertPath, clientCertPath, privKeyPath):
    def __init__(self):
        Cmd.__init__(self)

        # Disable CLI level arguments
        self.allow_cli_args = False

        # Enable debug - prints trace in case there is an issue
        self.debug = True

        # Remove the unused built-in commands from help
        self.exclude_from_help.append('do_edit')
        self.exclude_from_help.append('do_pyscript')
        self.exclude_from_help.append('do_load')
        self.exclude_from_help.append('do_py')
        self.exclude_from_help.append('do_shell')

        # Normal stuff
        self.gClient = None
        self.modelMap= { "wifi-mac": "wifi/mac/openconfig-wifi-mac.yang",
                         "wifi-phy": "wifi/phy/openconfig-wifi-phy.yang",
                         "wifi-system": "wifi/system/openconfig-system-wifi-ext.yang",
                         "vlan": "vlan/openconfig-vlan.yang",
                         "interfaces": "interfaces/openconfig-interfaces.yang",
                         "acl": "acl/openconfig-acl.yang",
                         }

    def do_describe(self, e):
        if len(e) == 0 or e[0] != '/':
            print "Invalid path ...", e
            return

        modelDir = "public/release/models/"
        tkns = e[1:].split('/')
        if "-".join(tkns[0:2]) in self.modelMap:
            yangFile = modelDir +  self.modelMap['-'.join(tkns[0:2])]
            os.system("pyang -p %s -f tree %s" % (modelDir, yangFile))
        else:
            print "Model not found...", e

    def help_describe(self):
        print "Describes the model, schema of the path specified"
        print "Usage: describe <path>"
        print "Arugments:"
        print "\t<path>: Node path that needs description"
        print "\t        eg. /wifi/mac"

    connectParser = argparse.ArgumentParser()
    connectGrp = connectParser.add_argument_group()
    connectParser.add_argument('targetURL',  help='target\'s ip/url & port')
    connectGrp.add_argument('--tls', dest='cafile', help="path to server certificate")
    connectGrp2 = connectParser.add_argument_group()
    connectGrp2.add_argument('-u', '--username', dest='username', help="username")
    connectGrp2.add_argument('-p', '--password', dest='password', help="password")

    @with_argparser(connectParser)
    def do_connect(self, args):
        print args
        self.gClient = gNMIClient(args.targetURL, (args.cafile != None), args.cafile, None, None)

    def do_capabilities(self, e):
        if self.gClient is None:
            print "grpc not is down... help connect"
            return None
        resp = self.gClient.capabilitiesRequest()
        print resp

    def help_capabilities(self):
        print "Gets the capabilities of gNMI Target"
        print "Usage: capabilities"
        print "Arguments:\n\tNone\nOptions:\n\tNone"

    def do_get(self, e):
        if self.gClient is None:
            print "grpc is down... help connect"
            return None

        resp = self.gClient.getRequest(e)
        if resp is None:
            return
        for n in resp.notification:
            for u in n.update:
                print u.val.string_val
        print resp.notification[0].update[0].val.string_val

    def help_get(self):
        print "Gets the object based on the path"
        print "Usage: get <path>"
        print "Arguments:"
        print "\t<path>: Node path that should be retrieved"
        print "\t        eg. /wifi/mac/ssids[name=\"tsunami\"]"

    def do_subscribe(self, e):
        if self.gClient is None:
            print "grpc is down... help connect"
            return None

        self.gClient.subscribeRequest(e)

    def help_subscribe(self):
        print "Subscribe to a path/prefix"
        print "Usage: subscribe <path>"
        print "Arguments:"
        print "\t<path>: Node path that the client is interested in"
        print "\t        eg. /wifi/phy/radios/radio/neighbors"
        print "\t            Neightbors of all radios on a given wifi network"

#
# main
#
def main():
    cCli = gNMIClientCli()
    cCli.cmdloop()

# Starts here
if __name__ == '__main__':
    main()
