#!/bin/bash

# Importing useful functions for cc testing
if [ -f ./func.sh ]; then
 source ./func.sh
elif [ -f scripts/func.sh ]; then
 source scripts/func.sh
fi


echo_b "Query chaincode on org1/peer0..."
chaincodeQuery ${APP_CHANNEL} 1 0 ${MY_CC_NAME} ${D_CC_QUERY_ARGS}

echo_b "Query chaincode on org2/peer0..."
chaincodeQuery ${APP_CHANNEL} 2 0 ${MY_CC_NAME} ${D_CC_QUERY_ARGS}

echo_b "Query chaincode on org3/peer0..."
chaincodeQuery ${APP_CHANNEL} 3 0 ${MY_CC_NAME} ${D_CC_QUERY_ARGS}

echo_b "Query chaincode on org4/peer0..."
chaincodeQuery ${APP_CHANNEL} 4 0 ${MY_CC_NAME} ${D_CC_QUERY_ARGS}