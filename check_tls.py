from datetime import datetime
from kubernetes import client, config
import OpenSSL
import ssl
import json


def main():
    # k8s_config_file_path    = '/Users/radu.dragan/.kube/config'
    # config.load_kube_config(k8s_config_file_path)
    config.load_incluster_config()
    v1              = client.CoreV1Api()
    k8s_namespace   = 'radu-operspin'
    services        = v1.list_namespaced_service(namespace=k8s_namespace)
    for svc in services.items:
        spinnaker_svc=(svc.metadata.name + '.' + k8s_namespace + '.' + 'svc.cluster.local')
        spinnaker_ports=(svc.spec.ports[0].port)
        # print (spinnaker_svc)
        # print (spinnaker_ports)
        #print(spinnaker_svc, spinnaker_ports)    
        writeFileToJson(spinnaker_svc, spinnaker_ports)


def check_tls(hosts, ports):
    cert    = ssl.get_server_certificate((hosts, ports))
    print (cert)
    x509    = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM, cert)
    if ( x509 != '' ):
        print ( x509 )
        bytes   = x509.get_notAfter()
        subject = x509.get_subject()
        timestamp   = bytes.decode('utf-8')
        cn          = subject.CN
        expiryDate  = ((datetime.strptime(timestamp, '%Y%m%d%H%M%S%z').date().isoformat()))
        jsonOutput = {
            'common name' : cn,
            'expiry date' : expiryDate
        }
    else:
        print ('FAILURE')
    return jsonOutput

def writeFileToJson(spinnaker_svc, spinnaker_ports):
    output  =   []
    try:
        for x, y in zip(spinnaker_svc, spinnaker_ports):        
            output.append(check_tls(x, y))
            convertJson = json.dumps(output, sort_keys=True)
            createJson  = open('tls_expiry' + str(datetime.now().strftime('%Y_%m_%d_%H_%M_%S')) + '.json', "w")
            createJson.write(convertJson)
            createJson.close()
    except:
        pass
        print('Traceback exception!')



if __name__ == '__main__':
    main()