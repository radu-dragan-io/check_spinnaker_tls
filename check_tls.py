from datetime import datetime
from kubernetes import client, config
import OpenSSL
import ssl
import json


def main():
    config.load_incluster_config()
    v1              = client.CoreV1Api()
    k8s_namespace   = '${ namespace }'
    services        = v1.list_namespaced_service(namespace=k8s_namespace)
    service = []
    port    = []
    for svc in services.items:
        spinnaker_svc   = (svc.metadata.name + '.' + k8s_namespace + '.' + 'svc.cluster.local')
        spinnaker_ports = str(svc.spec.ports[0].port)
        service += [spinnaker_svc]
        port    += [spinnaker_ports] 
    check_tls(service, port)



def check_tls(service, port):
    transformToJson = []
    for x, y in zip(service, port):
        serverHost    = x
        serverPort    = y
        serverAddress = (serverHost, serverPort)
        try:
            cert          = ssl.get_server_certificate(serverAddress)
            x509          = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM, cert)
            bytes         = x509.get_notAfter()
            timestamp     = bytes.decode('utf-8')
            expiryDate    = ((datetime.strptime(timestamp, '%Y%m%d%H%M%S%z').date().isoformat()))
            jsonOutput    = {
                'serviceName' : serverHost,
                'expiryDate' : expiryDate
            },
            print(jsonOutput)
            transformToJson += [jsonOutput]
        except:
            continue
    SPINNAKER_PROPERTY_TLS_EXPIRY = json.dumps(transformToJson)
    print("SPINNAKER_PROPERTY_TLS_EXPIRY=" + SPINNAKER_PROPERTY_TLS_EXPIRY)


if __name__ == '__main__':
    main()