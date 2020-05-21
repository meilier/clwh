/*
 * Licensed to the Apache Software Foundation (ASF) under one
 * or more contributor license agreements.  See the NOTICE file
 * distributed with this work for additional information
 * regarding copyright ownership.  The ASF licenses this file
 * to you under the Apache License, Version 2.0 (the
 * "License"); you may not use this file except in compliance
 * with the License.  You may obtain a copy of the License at
 *
 * http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing,
 * software distributed under the License is distributed on an
 * "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
 * KIND, either express or implied.  See the License for the
 * specific language governing permissions and limitations
 * under the License.
 */

/*
 * The sample smart contract for documentation topic:
 * Writing Your First Blockchain Application
 */

package main

/* Imports
 * 4 utility libraries for formatting, handling bytes, reading and writing JSON, and string manipulation
 * 2 specific Hyperledger Fabric specific libraries for Smart Contracts
 */
import (
	"bytes"
	"encoding/json"
	"fmt"
	"strconv"

	"github.com/hyperledger/fabric/core/chaincode/shim"
	sc "github.com/hyperledger/fabric/protos/peer"
)

// Define the Smart Contract structure
type SmartContract struct {
}

// Define the car structure, with 4 properties.  Structure tags are used by encoding/json library
type DataProviderServiceInitial struct {
	ProbviderDataSize string `json:"providerdatasize"`
	UnitPrice         string `json:"unitprice"`
	ParticipantNumber string `json:"participantnumber"`
}

type Participant struct {
	Name          string `json:"name"`
	Datasize      string `json:"datasize"`
	ModelAccuracy string `json:"modelaccuracy"`
}

type Result struct {
	Spend string `json:"spend"`
}

/*
 * The Init method is called when the Smart Contract "fabcar" is instantiated by the blockchain network
 * Best practice is to have any Ledger initialization in separate function -- see initLedger()
 */
func (s *SmartContract) Init(APIstub shim.ChaincodeStubInterface) sc.Response {
	// Get the args from the transaction proposal
	args := APIstub.GetStringArgs()
	if len(args) != 4 {
		return shim.Error("Incorrect number of arguments. Expecting 5")
	}

	var pm = DataProviderServiceInitial{ProbviderDataSize: args[1], UnitPrice: args[2], ParticipantNumber: args[3]}

	pmAsBytes, _ := json.Marshal(pm)
	APIstub.PutState(args[0], pmAsBytes)
	pds, _ := strconv.Atoi(args[1])
	up, _ := strconv.Atoi(args[2])
	reward := pds * up
	APIstub.PutState("DataProvider", []byte(strconv.Itoa(reward)))

	return shim.Success(nil)
}

/*
 * The Invoke method is called as a result of an application request to run the Smart Contract "fabcar"
 * The calling application program has also specified the particular smart contract function to be called, with arguments
 */
func (s *SmartContract) Invoke(APIstub shim.ChaincodeStubInterface) sc.Response {

	// Retrieve the requested Smart Contract function and arguments
	function, args := APIstub.GetFunctionAndParameters()
	// Route to the appropriate handler function to interact with the ledger appropriately
	if function == "getInitial" {
		return s.getInitial(APIstub, args)
	} else if function == "addParticipant" {
		return s.addParticipant(APIstub, args)
	} else if function == "getSpend" {
		return s.getSpend(APIstub, args)
	} else if function == "getReward" {
		return s.getReward(APIstub, args)
	}

	return shim.Error("Invalid Smart Contract function name.")
}

func (s *SmartContract) getInitial(APIstub shim.ChaincodeStubInterface, args []string) sc.Response {

	if len(args) != 1 {
		return shim.Error("Incorrect number of arguments. Expecting 1")
	}

	pmAsBytes, _ := APIstub.GetState(args[0])
	return shim.Success(pmAsBytes)
}

func (s *SmartContract) addParticipant(APIstub shim.ChaincodeStubInterface, args []string) sc.Response {

	if len(args) != 3 {
		return shim.Error("Incorrect number of arguments. Expecting 3")
	}

	var p = Participant{Name: args[0], Datasize: args[1], ModelAccuracy: args[2]}

	pAsBytes, _ := json.Marshal(p)
	APIstub.PutState(args[0], pAsBytes)

	return shim.Success(nil)
}

func (s *SmartContract) getReward(APIstub shim.ChaincodeStubInterface, args []string) sc.Response {

	if len(args) != 1 {
		return shim.Error("Incorrect number of arguments. Expecting 1")
	}

	r, _ := APIstub.GetState(args[0])
	return shim.Success(r)
}

func (s *SmartContract) getSpend(APIstub shim.ChaincodeStubInterface, args []string) sc.Response {

	if len(args) != 1 {
		return shim.Error("Incorrect number of arguments. Expecting 1")
	}
	var flag int
	if args[0] == "A" {
		flag = 0
	} else if args[0] == "B" {
		flag = 1
	} else if args[0] == "C" {
		flag = 2
	} else {
		flag = 3
	}
	initAsBytes, _ := APIstub.GetState("Init")
	var dps DataProviderServiceInitial
	json.Unmarshal(initAsBytes, &dps)
	du, _ := strconv.Atoi(dps.UnitPrice)
	dpr, _ := strconv.Atoi(dps.ProbviderDataSize)
	dpa, _ := strconv.Atoi(dps.ParticipantNumber)
	avg := (du * dpr) / dpa
	//get all participan datasize and modelaccuracy
	var allP [4]Participant
	aAsBytes, _ := APIstub.GetState("A")
	json.Unmarshal(aAsBytes, &allP[0])
	bAsBytes, _ := APIstub.GetState("B")
	json.Unmarshal(bAsBytes, &allP[1])
	cAsBytes, _ := APIstub.GetState("C")
	json.Unmarshal(cAsBytes, &allP[2])
	dAsBytes, _ := APIstub.GetState("D")
	json.Unmarshal(dAsBytes, &allP[3])

	var quality [4]int
	sum := 0
	for i := 0; i <= 3; i++ {
		ad, _ := strconv.Atoi(allP[i].Datasize)
		am, _ := strconv.ParseFloat(allP[i].ModelAccuracy, 32)
		quality[i] = int(float64(ad) * am)
		sum = sum + quality[i]
	}

	spend := ((sum / dpa) - quality[flag]) * du
	//var r Result
	all := spend + avg
	fmt.Println("all is ", all)

	//r.Spend = string(all)
	//rAsBytes, _ := json.Marshal(r)

	var buffer bytes.Buffer
	buffer.WriteString("[")
	buffer.WriteString("{\"Spend\":")
	buffer.WriteString(strconv.Itoa(all))
	buffer.WriteString("}")
	buffer.WriteString("]")
	return shim.Success(buffer.Bytes())
}

// The main function is only relevant in unit test mode. Only included here for completeness.
func main() {

	// Create a new Smart Contract
	err := shim.Start(new(SmartContract))
	if err != nil {
		fmt.Printf("Error creating new Smart Contract: %s", err)
	}
}
