# Shyam Jivandas Rabadiya
# 1001873983
import os
import pickle
import socket
import time
import pandas as pd

port = 60024  # Reserving a port for server B.
s = socket.socket()  # Creating a socket object
host = socket.gethostname()  # local machine name
s.bind((host, port))  # Binding to the port of server B
s.listen(5)  # wait time for client connection

dataframe = pd.DataFrame()  # to represent the result in 2-d form

print('Server B is up and running....')  # to ensure the server B is running

while True:
  conn, addr = s.accept()  # Establishing connection with the client
  print('Got connection from', addr)

  current_directory = os.getcwd()  # to get the current directory
  server_b_directory = "directory_b"

  files_list = os.listdir(os.path.join(current_directory, server_b_directory))  # to get all the files from the
  # directory_b

  for file in files_list:  # for loop for the files list to get each file information
    status = os.stat(os.path.join(current_directory, server_b_directory, file))  # to get the details of the file
    dataframe = dataframe.append({"File name": file, "size(kb)": float(status.st_size) / 1000,
                                  "Modified date": time.ctime(status.st_mtime)},
                                 ignore_index=True)  # appending the each file information

  data = pickle.dumps(dataframe)  # to store the dataframe in the same way as it is
  print(pickle.loads(data))  # to print the files in directory b
  conn.sendall(data)  # sending the details of all files present in directory_b to server A
  dataframe.drop(dataframe.index, inplace=True)
  del data
  print('Done sending files information from server B to server A')
