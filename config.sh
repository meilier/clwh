export FABRIC_CFG_PATH=$PWD

# generate orderer gensis block
configtxgen -channelID testchainid -profile FourOrgsOrdererGenesis -outputBlock ./channel-artifacts/orderer.genesis.block

# generate channel tx
configtxgen -profile FourOrgsChannel -outputCreateChannelTx ./channel-artifacts/mychannel.tx -channelID mychannel

# update org anchor peer
configtxgen --profile FourOrgsChannel --outputAnchorPeersUpdate ./channel-artifacts/Org1MSPanchors.tx -channelID mychannel -asOrg Org1MSP
configtxgen --profile FourOrgsChannel --outputAnchorPeersUpdate ./channel-artifacts/Org2MSPanchors.tx -channelID mychannel -asOrg Org2MSP
configtxgen --profile FourOrgsChannel --outputAnchorPeersUpdate ./channel-artifacts/Org3MSPanchors.tx -channelID mychannel -asOrg Org3MSP
configtxgen --profile FourOrgsChannel --outputAnchorPeersUpdate ./channel-artifacts/Org4MSPanchors.tx -channelID mychannel -asOrg Org4MSP