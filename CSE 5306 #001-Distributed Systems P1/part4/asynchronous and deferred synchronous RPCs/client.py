import json
import socket
import sys
import threading

Sip = "127.0.0.1"
Sport = 8080

Sync = 0
Async = 1
Deferred = 2
Invoke = 1
RResult = 2
Ack = 1
RESPONSE_RESULT = 2


class ASYrpc:
    def __init__(self, function, args):
        self.function = function
        self.args = args
        self.rpc_type = Async
        self.computation_id = None
        self.result = None

    def invoke(self):
       
        request = {
            "function": self.function,
            "args": self.args,
            "rpc_type": self.rpc_type,
            "request_type": Invoke,
        }
        tsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tsock.connect((Sip, Sport))
        tsock.send(json.dumps(request).encode())
        response = tsock.recv(65536).decode()
        response = json.loads(response)
        tsock.close()

        if "error" in response:
            raise RuntimeError(response["error"])

        if "response_type" not in response:
            raise RuntimeError("No response from server")

        self.computation_id = response["token"]

    def get_result(self):
        request = {
            "rpc_type": self.rpc_type,
            "token": self.computation_id,
            "request_type": RResult,
        }

        tsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tsock.connect((Sip, Sport))
        tsock.send(json.dumps(request).encode())
        response = tsock.recv(65536).decode()
        response = json.loads(response)
        tsock.close()
        if "error" in response:
            raise RuntimeError(response["error"])
        if "response_type" not in response:
            raise ValueError("No response received from server")

        self.result = response["result"]
        return self.result


class DefRPC:
    def __init__(self, function, args):
        self.function = function
        self.args = args
        self.rpc_type = Deferred
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((Sip, Sport))

    def __del__(self):
        self.sock.close()

    def get_result(self):
        response = self.sock.recv(65536).decode()

        response = json.loads(response)
        if "error" in response:
            raise RuntimeError(response["error"])
        if "response_type" not in response:
            raise RuntimeError("no response received from server")

        result = response.get("result")
        if result is None:
            raise RuntimeError("error in result")
        return response["result"]

    def invoke(self, parallel_function=None, args=[]):
        request = {
            "function": self.function,
            "args": self.args,
            "rpc_type": self.rpc_type,
            "request_type": Invoke,
        }
        self.sock.send(json.dumps(request).encode())
        if parallel_function is not None:
            thread = threading.Thread(target=parallel_function, args=args)
            thread.start()

        result = self.get_result()
        print(f"received from server: {result}")
        thread.join()
        return result
