#!/bin/bash

# Importing useful functions for cc testing
if [ -f ./func.sh ]; then
 source ./func.sh
elif [ -f scripts/func.sh ]; then
 source scripts/func.sh
fi



# Instantiate chaincode in the channel, executed once on any node is enough
# (once for each channel is enough, we make it concurrent here)
echo_b "=== Instantiating chaincode on channel ${APP_CHANNEL}... ==="

# Instantiate at org1.peer0 and org2.peer0, actually it can be triggered once per channel
chaincodeInstantiate mychannel 1 0 psc_cc 1.0 '{"Args":["init","ParameterInitial","10","32","16","0.01"]}'
#chaincodeInstantiate "${APP_CHANNEL}" 2 0 ${CC_NAME} ${CC_INIT_VERSION} ${CC_INIT_ARGS}

echo_g "=== Instantiate chaincode on channel ${APP_CHANNEL} done ==="

echo