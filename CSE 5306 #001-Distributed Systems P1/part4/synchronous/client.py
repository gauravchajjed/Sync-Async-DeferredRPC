import json
import socket
import sys

Sip = socket.gethostbyname(socket.gethostname())
Sport = 8080

def rpc(fn, args):    
    request = {"fn": fn, "args": args}
    tsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tsock.connect((Sip, Sport))
    tsock.send(json.dumps(request).encode())
    response = tsock.recv(65536).decode()
    tsock.close()
    response = json.loads(response)
    if "error" in response:
        raise RuntimeError(response["error"])
    return response["result"]

def main():

 i = int(input("Enter first number"))
 j = int(input("Enter second number"))
 print(rpc("add", args=[i,j]))

 print("\nsort([10, 6, 4, 7, 1])")
 print(rpc("sort", args=[[10, 6, 4, 7, 1]]))



if __name__ == "__main__":
    main()