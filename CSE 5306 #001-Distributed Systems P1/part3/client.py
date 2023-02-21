# Shyam Jivandas Rabadiya
# 1001873983
import pickle
import socket
import sys

client = socket.socket()  # Creating a socket object
host = socket.gethostname()  # local machine name
port = 60001  # Reserve a port for your service

client.connect((host, port))

while True:
  d=pickle.dumps((sys.argv)) #to get the file index and lock/unlock operation
  client.sendall(d)


  data = client.recv(4096)
  result = pickle.loads(data)
  print(result)

