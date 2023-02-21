import time

from client import ASYrpc


def main():
 

   
    print("\n waiting..\n")
    time.sleep(12)

    print("Requesting to add(1, 2)")
    add_rpc = ASYrpc("add", args=[1, 2])
    add_rpc.invoke()

   
    print("Results = {}".format(add_rpc.get_result()))
  

if __name__ == "__main__":
    main()
