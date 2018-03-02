#
# gNMI Target
#

import argparse
import time
from concurrent import futures
import grpc

import gnmi_pb2
import gnmi_pb2_grpc

from gNMIUtils import gNMIUtils
from ocShim import ocShim


#
# class gNMITargetServicer
#
class gNMITargetServicer(gnmi_pb2_grpc.gNMIServicer):

    def __getCapabilitiesResponseObj(self):
        capResp = gnmi_pb2.CapabilityResponse()
        supModel = gnmi_pb2.ModelData(name="my_model", organization="My Company Inc", version="1.0")
        capResp.supported_models.extend([supModel])
        capResp.supported_encodings.extend(gnmi_pb2.JSON)
        capResp.gNMI_version = "GNMI Version 1.0"
        return capResp

    def __processGetRequestObj(self, reqGetObj):
        pathArr = []

        t = reqGetObj.type
        pathArr.extend(gNMIUtils.extractPathObj(reqGetObj.prefix))
        #FIXME: walk thru all the paths
        pathArr.extend(gNMIUtils.extractPathObj(reqGetObj.path[0]) if len(reqGetObj.path) > 0 else None)
        respStr = ocShim.processGetRequest(pathArr)

        # Now Build the get reponse
        getResp = gnmi_pb2.GetResponse()
        notif = getResp.notification.add()
        notif.timestamp = int(time.time())
        gNMIUtils.fillPrefix(pathArr, notif.prefix)
        update = notif.update.add()
        gNMIUtils.fillPath(pathArr[len(pathArr)-1], update.path)
        update.val.string_val = respStr

        return getResp

    def __processSubscribeRequestObj(self, reqSubObj):
        for req in reqSubObj:
            #print req
            pathArr = []
            pathArr.extend(gNMIUtils.extractPathObj(req.subscribe.prefix))
            pathArr.extend(gNMIUtils.extractPathObj(req.subscribe.subscription[0].path))

            respStr = ocShim.processSubscribeRequest(pathArr)

            subResp = gnmi_pb2.SubscribeResponse()
            subResp.sync_response = True
            subResp.update.timestamp = int(time.time())
            gNMIUtils.fillPrefix(pathArr, subResp.update.prefix)
            update = subResp.update.update.add()
            gNMIUtils.fillPath(pathArr[len(pathArr)-1], update.path)
            update.val.string_val = respStr
            yield subResp

    # gNMI Services Capabilities Routine
    def Capabilities(self, request, context):
        print "Recv'ed Capabiality Request"
        return self.__getCapabilitiesResponseObj()

    # gNMI Services Get Routine
    def Get(self, request, context):
        print "Recv'ed Get Request"
        return self.__processGetRequestObj(request)

    # gNMI Services Subscribe Routine
    def Subscribe(self, request, context):
        print "Recv'ed Subscribe Request"
        return self.__processSubscribeRequestObj(request)

#
# class gNMITarget
#
class gNMITarget:
    """gNMI Wrapper for the Server/Target"""
    def __init__(self, targetUrl, tlsEnabled, caCertPath, privKeyPath):
        self.grpcServer = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        gnmi_pb2_grpc.add_gNMIServicer_to_server(gNMITargetServicer(), self.grpcServer)

        if tlsEnabled == True:
            # secure connection
            print privKeyPath, caCertPath
            with open(privKeyPath) as f:
                privateKey = f.read()
            with open(caCertPath) as f:
                certChain = f.read()
            credentials = grpc.ssl_server_credentials(((privateKey, certChain, ), ))
            self.grpcServer.add_secure_port(targetUrl, credentials)
        else:
            # insecure connection
            self.grpcServer.add_insecure_port(targetUrl)

    def run(self):
        self.grpcServer.start()
        try:
            while True:
                time.sleep(60*60*24)
        except KeyboardInterrupt:
            self.grpcServer.stop(0)

#
# main
#
def main():
    parser = argparse.ArgumentParser()
    parserGrp = parser.add_argument_group("secure grpc")
    parser.add_argument('targetURL', help="target url, typically localhost:<port>")
    parserGrp.add_argument('--tls', action="store_true", help="enable tls connection")
    parserGrp.add_argument('--cert', help="path to the certificate")
    parserGrp.add_argument('--pvtkey', help="path to the private key file")
    args = parser.parse_args()

    print args

    gTarget = gNMITarget(args.targetURL, args.tls, args.cert, args.pvtkey)
    gTarget.run()

# Starts here
if __name__ == '__main__':
    main()
