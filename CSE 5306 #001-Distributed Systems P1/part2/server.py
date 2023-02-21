
import base64
import socket
import sys
from pathlib import Path
from threading import Thread

Sip = "0.0.0.0"
Sport = 8080
Bsize = 65536
Conlimit = 1024


class WorkerThread(Thread):
    def __init__(self, ip, port, conn):
        Thread.__init__(self)
        self.client_ip = ip
        self.client_port = port
        self.conn = conn

    def run(self):
        msg = self.conn.recv(Bsize)
        tok = msg.split(b"\n", maxsplit=2)
        command = tok[0].decode().strip().lower()

        if command == "upload":
            filename = tok[1].decode().strip()
            file_data = tok[2]
            Path("upload/").mkdir(parents=True, exist_ok=True)
            Path("upload/{}".format(filename)).write_bytes(file_data)
            print(f" Uploaded '{filename}'")

        elif command == "download":
            filename = tok[1].decode().strip()
            file = Path("upload/{}".format(filename))
            if file.is_file():
                self.conn.send(file.read_bytes())
                print(f"Downloaded '{filename}'")

        elif command == "delete":
            filename = tok[1].decode().strip()
            file = Path("upload/{}".format(filename))
            if file.is_file():
                file.unlink()
                print(f" Deleted '{filename}'")

        elif command == "rename":
            filename = tok[1].decode().strip()
            new_filename = tok[2].decode().strip()
            file = Path("upload/{}".format(filename))
            new_file = Path("upload/{}".format(new_filename))
            if file.is_file():
                file.rename(new_file)
                print(f"Renamed '{filename}' to '{new_filename}'")


def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((Sip, Sport))
    sock.listen(Conlimit)
    print(f"Server {Sip}:{Sport}")
    while True:
        (conn, (client_ip, client_port)) = sock.accept()
        worker = WorkerThread(client_ip, client_port, conn)
        worker.start()


if __name__ == "__main__":
    main()
