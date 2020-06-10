import asyncio
from hfc.fabric import Client
import torch
import os
import json
import numpy as np
import os
from util.utils import network_json_path
from util.utils import project_path



class ChainInterface:
    def __init__(self):
        super().__init__()
        self.loop = asyncio.get_event_loop()
        self.cli = Client(net_profile=network_json_path)
        self.org1_admin = self.cli.get_user('org1.example.com', 'Admin')
        self.org2_admin = self.cli.get_user('org2.example.com', 'Admin')
        self.org3_admin = self.cli.get_user('org3.example.com', 'Admin')
        self.org4_admin = self.cli.get_user('org4.example.com', 'Admin')
        self.admin_list = [self.org1_admin,self.org2_admin,self.org3_admin,self.org4_admin]
        self.org_peers=[['peer0.org1.example.com'], ['peer0.org2.example.com'], ['peer0.org3.example.com'], ['peer0.org4.example.com']]

        # Make the client know there is a channel in the network
        self.cli.new_channel('mychannel')
        # GOPATH setting is only needed to use the example chaincode inside sdk
        gopath_bak = os.environ.get('GOPATH', '')
        gopath = os.path.normpath(os.path.join(
                            project_path + "op_peer/",
                            'chaincode'
                            ))
        os.environ['GOPATH'] = os.path.abspath(gopath)
    
    # Install  Chaincode to Peers
    def ps_chaincode_install(self):
        print("start to install chaincode")
        orgs = list(self.cli.get_net_info('organizations').keys())[1:]
        for org in orgs:       
            org_admin = self.cli.get_user(org, "Admin")
            responses = self.loop.run_until_complete(self.cli.chaincode_install(
                        requestor=org_admin,
                        peers=['peer0.' + org],
                        cc_path='github.com/psc_cc',
                        cc_name='psc_cc',
                        cc_version='v1.0'
                        ))
        return responses

    def ps_chaincode_instantiate(self,args_list):
        # The response should be true if succeed
        # Instantiate Chaincode in Channel, the response should be true if succeed
        
        # policy, see https://hyperledger-fabric.readthedocs.io/en/release-1.4/endorsement-policies.html
        print("start to instantiate chaincode")
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
        response = self.loop.run_until_complete(self.cli.chaincode_instantiate(
                    requestor=self.org1_admin,
                    channel_name='mychannel',
                    peers=['peer0.org1.example.com'],
                    args=args_list,
                    cc_name='psc_cc',
                    cc_version='v1.0',
                    cc_endorsement_policy=policy, # optional, but recommended
                    collections_config=None, # optional, for private data policy
                    transient_map=None, # optional, for private data
                    wait_for_event=True # optional, for being sure chaincode is instantiated
                    ))
        return response

    def ps_chaincode_query(self, fcn_name, args_list, peer_id):
        # Query a chaincode
        # The response should be true if succeed
        response = self.loop.run_until_complete(self.cli.chaincode_query(
                    requestor=self.admin_list[peer_id + 1],
                    channel_name='mychannel',
                    peers=self.org_peers[peer_id + 1],
                    args=args_list,
                    cc_name='psc_cc',
                    fcn=fcn_name
                    ))
        return response

    def ps_chaincode_invoke(self, fcn_name, args_list, peer_id):
        # Invoke a chaincode
        # The response should be true if succeed
        response = self.loop.run_until_complete(self.cli.chaincode_invoke(
                    requestor=self.admin_list[peer_id + 1],
                    channel_name='mychannel',
                    peers=self.org_peers[peer_id + 1],
                    args=args_list,
                    cc_name='psc_cc',
                    fcn=fcn_name,
                    transient_map=None, # optional, for private data
                    wait_for_event=True, # for being sure chaincode invocation has been commited in the ledger, default is on tx event
                    wait_for_event_timeout=40,
                    #cc_pattern='^invoked*' # if you want to wait for chaincode event and you have a `stub.SetEvent("invoked", value)` in your chaincode
                    ))
        return response

    def ps_chaincode_invoke_ps(self, fcn_name, args_list):
        # Invoke a chaincode
        # The response should be true if succeed
        response = self.loop.run_until_complete(self.cli.chaincode_invoke(
                    requestor=self.org4_admin,
                    channel_name='mychannel',
                    peers=['peer0.org4.example.com'],
                    args=args_list,
                    cc_name='psc_cc',
                    fcn=fcn_name,
                    transient_map=None, # optional, for private data
                    wait_for_event=True, # for being sure chaincode invocation has been commited in the ledger, default is on tx event
                    wait_for_event_timeout=40,
                    #cc_pattern='^invoked*' # if you want to wait for chaincode event and you have a `stub.SetEvent("invoked", value)` in your chaincode
                    ))
        return response

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
            