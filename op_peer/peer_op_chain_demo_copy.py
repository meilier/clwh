import asyncio
from hfc.fabric import Client


loop = asyncio.get_event_loop()

orgs = ["org1.example.com", "org2.example.com", "org3.example.com", "org4.example.com"]

cli = Client(net_profile="/Users/xingweizheng/github/clwh/op_peer/network.json")
org1_admin = cli.get_user('org2.example.com', 'Admin')



# Make the client know there is a channel in the network
cli.new_channel('mychannel')

# Install Example Chaincode to Peers
# GOPATH setting is only needed to use the example chaincode inside sdk
import os
gopath_bak = os.environ.get('GOPATH', '')
gopath = os.path.normpath(os.path.join(
                      os.path.dirname(os.path.realpath('__file__')),
                      'chaincode'
                     ))
os.environ['GOPATH'] = os.path.abspath(gopath)



# Query a chaincode
args = ['b']
# The response should be true if succeed
response = loop.run_until_complete(cli.chaincode_query(
               requestor=org1_admin,
               channel_name='mychannel',
               peers=['peer0.org2.example.com'],
               args=args,
               cc_name='example_cc'
               ))
            