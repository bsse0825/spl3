import socket
import sys
import os
import re
import string

import NK_Prediction1
import helper

# UNIX SOCKET ADDRESS 
server_address = './uds_socket'

# SOCKET BUFFER MAX SIZE
SOCKET_MAX_BUFFER = 1024

def initPredictionModel():
        NK_Prediction1.initModel()
        helper.startup()
        return 0


def predict(banglisgWord):
	return NK_Prediction1.getPrediction(banglisgWord)
def checkWord(banglaWord):
        return helper.check([banglaWord])
purifyWord_regex = re.compile('[^a-zA-Z]')
def purifyWord(word):
        v = purifyWord_regex.sub('', word)
        return v.lower()


def runPrediction(banglishSentence):
        prediction = ''
        banglishWords = banglishSentence.split(' ')
        for banglishWord in banglishWords:
                prediction = prediction + ' ' + predict(purifyWord(banglishWord))
        return prediction


def processRequest():
        # Make sure the socket does not already exist
        try:
                os.unlink(server_address)
        except OSError:
                if os.path.exists(server_address):
                        raise

        # Create a UDS socket
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)


        # Bind the socket to the port
        print('Waiting for request : ',server_address)
        sock.bind(server_address)

        # Listen for incoming connections
        sock.listen(1)

        while True:
                # Wait for a connection
                connection, client_address = sock.accept()
                try:
                        print('Request from : ', client_address)

                        totalData = ""
                        # Receive the data in small chunks and retransmit it
                        while True:
                                data = connection.recv(SOCKET_MAX_BUFFER)
                                
                                if data:
                                        dataStr = data.decode('utf-8')
                                        totalData = totalData + dataStr
                                        if len(data) < SOCKET_MAX_BUFFER:
                                                break
                                else:
                                        break
                        
                        if dataStr == "I Quit":
                                break

                        print("Requested data: " + totalData)

                        result = runPrediction(dataStr)
                        error, suggestionResult = checkWord(result.split()[len(result.split())-1])
                        #print('Error',error)
                        #print('sugestion',suggestionResult)
                        resultsug = ''
                        if suggestionResult != None:
                                for sug in suggestionResult:
                                        resultsug += ' '+sug
                        result = str(len(result.split()))+' '+result
                        resultArray = result.encode('utf-8')
                        connection.sendall(resultArray)
                        print(resultsug)
                        connection.sendall(resultsug.encode('utf-8'))
                        print("Result Sent: " + result)

                finally:
                        # Clean up the connection
                        connection.close()



if initPredictionModel() != 0:
        print("Prediction model initilization unsuccessfull.")
        exit(1)

processRequest()
exit(0)
