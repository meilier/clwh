
from hfc.fabric import Client
import torch
import os
import json
import numpy as np



orgs = ["org1.example.com", "org2.example.com", "org3.example.com", "org4.example.com"]

cli = Client(net_profile="/Users/xingweizheng/github/clwh/op_peer/network.json")
org2_admin = cli.get_user('org2.example.com', 'Admin')

empty_dict = torch.load("/Users/xingweizheng/github/clwh/mnist-6000-1000-base.pth")

dict_name = ['fc.0.weight','fc.2.weight','fc.4.weight','fc.6.weight','fc.0.bias','fc.2.bias','fc.4.bias','fc.6.bias']


# for name in dict_name:
#     empty_dict[name] = empty_dict[name].tolist()


# args = ['a', json.dumps(empty_dict)]
# print("he")
# exit(0)

# Make the client know there is a channel in the network
cli.new_channel('mychannel')

# Install Example Chaincode to Peers
# GOPATH setting is only needed to use the example chaincode inside sdk
import os
gopath_bak = os.environ.get('GOPATH', '')
gopath = os.path.normpath(os.path.join(
                      "/Users/xingweizheng/github/clwh/op_peer/",
                      'chaincode'
                     ))
os.environ['GOPATH'] = os.path.abspath(gopath)

# The response should be true if succeed
for org in orgs:
    org_admin = cli.get_user(org, "Admin")
    cli.chaincode_install(
                requestor=org_admin,
                peers=['peer0.' + org],
                cc_path='github.com/psc_cc',
                cc_name='psc_cc',
                cc_version='v1.0'
                )

# Instantiate Chaincode in Channel, the response should be true if succeed
args = ['ParameterInitial','10','32','16','0.01']

# policy, see https://hyperledger-fabric.readthedocs.io/en/release-1.4/endorsement-policies.html
policy = {
    'identities': [
        {'role': {'name': 'member', 'mspId': 'org1MSP'}},
        {'role': {'name': 'member', 'mspId': 'Org2MSP'}},
        {'role': {'name': 'member', 'mspId': 'Org3MSP'}},
        {'role': {'name': 'member', 'mspId': 'Org4MSP'}},
    ],
    'policy': {
        '1-of': [
            {'signed-by': 0},
            {'signed-by': 1},
            {'signed-by': 2},
            {'signed-by': 3},
        ]
    }
}
cli.chaincode_instantiate(
               requestor=org2_admin,
               channel_name='mychannel',
               peers=['peer0.org2.example.com'],
               args=args,
               cc_name='psc_cc',
               cc_version='v1.0',
               cc_endorsement_policy=policy, # optional, but recommended
               collections_config=None, # optional, for private data policy
               transient_map=None, # optional, for private data
               wait_for_event=True # optional, for being sure chaincode is instantiated
               )


# Query a chaincode
args = ['ParameterInitial']
# The response should be true if succeed
cli.chaincode_query(
               requestor=org2_admin,
               channel_name='mychannel',
               peers=['peer0.org2.example.com'],
               args=args,
               cc_name='psc_cc',
               fcn='getParameter'
               )


# Invoke a chaincode

for name in dict_name:
    empty_dict[name] = empty_dict[name].tolist()

gd = json.dumps(empty_dict)

li = [i for i in range(100000)]
args = ['a', gd]
# The response should be true if succeed
print("**********start************")
cli.chaincode_invoke(
               requestor=org2_admin,
               channel_name='mychannel',
               peers=['peer0.org2.example.com'],
               args=args,
               cc_name='psc_cc',
               fcn='addGradientData',
               transient_map=None, # optional, for private data
               wait_for_event=True, # for being sure chaincode invocation has been commited in the ledger, default is on tx event
               #cc_pattern='^invoked*' # if you want to wait for chaincode event and you have a `stub.SetEvent("invoked", value)` in your chaincode
               )
print("**********over************")

# Query a chaincode
# args = ['a']
# # The response should be true if succeed
# response = loop.run_until_complete(cli.chaincode_query(
#                requestor=org2_admin,
#                channel_name='mychannel',
#                peers=['peer0.org2.example.com'],
#                args=args,
#                cc_name='psc_cc',
#                fcn='getGradientData'
#                ))


            