import socket
import sys
import time

# Connect the socket to the port where the server is listening
server_address = './uds_socket'

while True:
    data = input("Data to send? <END> to end >> ")

    if data == '<END>':
        break

    print("Going to send "+data)

    # Create a UDS socket
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.settimeout(4.0)

    try:
        sock.connect(server_address)
        
        ar = bytearray(data, "utf-8")

        sock.sendall(ar)
        
        time.sleep(.02)

        resultData = sock.recv(32)
        resultStr = resultData.decode('utf-8')
        print("Result : "+resultStr)
    except socket.error as e:
        print ("Error occurred, ")
        print(e)

    finally:
        print ('closing socket')
        sock.close()

