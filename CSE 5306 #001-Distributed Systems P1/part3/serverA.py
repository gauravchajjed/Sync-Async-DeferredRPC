# Shyam Jivandas Rabadiya
# 1001873983
import filecmp
import os
import pickle
import socket
import time

import dirsync
import filelock
import pandas as pd
from watchdog.events import PatternMatchingEventHandler
from watchdog.observers import Observer

port = 60001  # Reserving a port for server A
server_a = socket.socket()  # For server A we are creating a socket object
host = socket.gethostname()  # naming local machine
server_a.bind((host, port))  # Binding to the port of server A
server_a.listen(5)  # client connection wait time
send_files_to_client = False
print('Server A is running....')  # to ensure that server A is running
file_list_with_operations = []  # to store the file indexes and lock/unlock operations


def sync_directory():
  path = os.getcwd() + '/directory_a/'
  copyto = os.getcwd() + '/directory_b/'

  if len(file_name_list) > 0:
    dirsync.sync(copyto, path, 'sync', ignore=file_name_list)  # ignoring the files which are locked at directory_a
  else:
    dirsync.sync(copyto, path, 'sync')
    dirsync.sync(path, copyto, 'sync')


def on_created(event):
  sync_directory()
  if compare_directories.common_files:  # checking and comparing the common files in both the directories
    for common_file in compare_directories.common_files:
      path_directory_a = os.path.join(current_directory, server_a_directory, common_file)
      path_directory_b = os.path.join(current_directory, server_b_directory, common_file)
      if os.path.isfile(path_directory_a) and os.path.isfile(path_directory_b):
        directory_a_time = time.ctime(
          os.stat(os.path.join(current_directory, server_a_directory, common_file)).st_mtime)
        directory_b_time = time.ctime(
          os.stat(
            os.path.join(current_directory, server_b_directory, common_file)).st_mtime)
        if directory_a_time < directory_b_time and directory_a_time != directory_b_time:  # comparing the modified time between the two files
          print(common_file == file_name)
          path = os.path.join(current_directory, server_a_directory, common_file)
          if os.path.isfile(path and (common_file == file_name and operation != 'lock')):
            os.remove(path)  # removing the oldest modified file from the directory
          else:
            path = os.path.join(current_directory, server_b_directory, common_file)
            if os.path.isfile(path and (common_file == file_name and operation != 'lock')):
              os.remove(path)  # removing the oldest modified file from the directory
        elif directory_a_time != directory_b_time:
          path = os.path.join(current_directory, server_b_directory, common_file)
          if os.path.isfile(path and (common_file == file_name and operation != 'lock')):
            os.remove(path)  # removing the oldest modified file from the directory


def on_deleted(event):
  directory_a_path = os.getcwd() + '/directory_a/'
  directory_b_path = os.getcwd() + '/directory_b/'

  a_path = os.path.join(directory_a_path, os.path.basename(event.src_path))

  b_path = os.path.join(directory_b_path, os.path.basename(event.src_path))

  file_name_to_be_deleted = os.path.basename(event.src_path)
  # checking if directory has the file to delete
  if file_name_to_be_deleted not in file_name_list:
    if os.path.isfile(a_path):
      os.remove(a_path)
    elif os.path.isfile(b_path):
      os.remove(b_path)


def on_modified(event):
  print(event.src_path + " has been modified")


while True:

  dataframe = pd.DataFrame()  # to represent the result in 2-d form
  conn, addr = server_a.accept()  # Establishing connection with client
  print('Got connection from server1', addr)

  data_from_client = conn.recv(4096)
  print(pickle.loads(data_from_client))
  loaded_data_from_client = pickle.loads(data_from_client)

  server_b = socket.socket()  # Create a socket object for server B
  port = 60024  # Reserving a port for server B
  server_b.connect((host, port))  # Connecting to server B

  data = server_b.recv(4096)
  data_from_server_b = pickle.loads(data)  # to get the list of files from server b.py directory

  current_directory = os.getcwd()  # to get the current directory
  server_a_directory = "directory_a"
  server_b_directory = "directory_b"

  files_list = os.listdir(os.path.join(current_directory, "directory_a"))  # to get all the files from the directory_a

  compare_directories = filecmp.dircmp(os.getcwd() + "/" + server_a_directory, os.getcwd() + "/" + server_b_directory)
  # to compare the files in directories

  patterns = ["*"]
  ignore_patterns = None
  ignore_directories = False
  case_sensitive = True
  my_event_handler = PatternMatchingEventHandler(patterns, ignore_patterns, ignore_directories, case_sensitive)
  # events for the file modification changes
  my_event_handler.on_created = on_created  # event for the new file added in directory
  my_event_handler.on_deleted = on_deleted  # event for the new file deleted in directory
  my_event_handler.on_modified = on_modified  # event for the new file modified in directory

  go_recursively = True

  observer_for_directory_a = Observer()  # watcher for the file changes in the directory a
  observer_for_directory_a.schedule(my_event_handler, current_directory + "/directory_a", recursive=go_recursively)
  observer_for_directory_a.start()  # starting the watcher for directory a

  observer_for_directory_b = Observer()  # watcher for the file changes in the directory b
  observer_for_directory_b.schedule(my_event_handler, current_directory + "/directory_b", recursive=go_recursively)
  observer_for_directory_b.start()  # starting the watcher for directory b

  dataframe = data_from_server_b  # appending the server B files list to server A

  print(dataframe)  # to print the files from directory a

  if len(compare_directories.same_files) != len(os.listdir(os.path.join(current_directory, "directory_a"))) or len(
    compare_directories.same_files) != len(os.listdir(os.path.join(current_directory, "directory_b"))):  # if file
    # synchronization is not yet applied
    for file in files_list:  # for loop for the files list to get each file information
      path = os.path.join(current_directory, server_a_directory, file)
      if os.path.isfile(path) and file not in compare_directories.same_files:
        status = os.stat(os.path.join(current_directory, server_a_directory, file))  # to get the details of the file
        dataframe = dataframe.append({"File name": file, "size(kb)": float(status.st_size) / 1000,
                                      "Modified date": time.ctime(status.st_mtime)},
                                     ignore_index=True)  # appending the each file information
        print(pickle.loads(pickle.dumps(dataframe)))

  data_for_client = dataframe.sort_values('File name').reset_index().drop(
    columns='index')  # sorting the files list by file name

  operation = ""  # lock/unlock operation given by user
  file_name_list = []  # file names which are locked
  file_list_with_operations.append(loaded_data_from_client)
  if (len(file_name_list)) == 0:
    data_for_client.insert(len(data_for_client.columns), '', '')  # to add the operation column for the first time
  if len(loaded_data_from_client) > 2:
    selected_index = int(loaded_data_from_client[1])  # get the index given by the user to lock/unlock
    file_name = data_for_client.iloc[selected_index]['File name']  # get the file name to lock/unlock
    operation = loaded_data_from_client[2]  # get the operation given by the user i.e lock/unlock
  for file_list_with_operation in file_list_with_operations:  # to get the operations for each of the files
    if len(file_list_with_operation) > 2:
      selected_index_file = int(file_list_with_operation[1])  # get the index of a particular file to lock/unlock
      file_name_with_operation = data_for_client.iloc[selected_index_file][
        'File name']  # get the file name of a particular file to lock/unlock
      operation = file_list_with_operation[2]  # to get the operations of file
      if operation == 'lock':  # if it is locked add to the file names
        file_name_list.append(file_name_with_operation)
      elif operation == 'unlock':  # if it is unlocked remove from the file names
        if file_name_with_operation in file_name_list:
          file_name_list.remove(file_name_with_operation)
          file_list_with_operations.remove(file_list_with_operation)

      #to get the duplicated of files present in both the directories as one of the file is locked
      index = data_for_client.index
      condition = data_for_client["File name"] == file_name_with_operation
      file_name_indices = index[condition]
      file_name_indices_list = file_name_indices.tolist()
      for i in file_name_indices_list:
        if i != selected_index_file:
          data_for_client.drop(i, inplace=True) #delete the file which is not locked
          data_for_client.reset_index(inplace=True) #resetting the datframe index
        else:
          data_for_client.ix[selected_index_file, len(data_for_client.columns) - 1] = operation # adding the lock/unlock column
  if 'level 0' in dataframe.columns:
    data_for_client.droplevel('level_0', axis=1) #removing the level 0 column
  if 'index' in dataframe.columns:
    data_for_client.droplevel('index', axis=1) #removing the index column
  data_for_client = pickle.dumps(data_for_client)  # to store the dataframe in the same way as it is
  print(pickle.loads(pickle.dumps(dataframe)))
  conn.sendall(
    data_for_client)  # sending the details of all files in a sorted way present in directory_a and directory_b to
  # the client

  del dataframe  # clearing dataframe
  del data_for_client

  print('The file names from server B and server A are sorted and sent to client')
