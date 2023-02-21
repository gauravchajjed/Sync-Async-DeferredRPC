import base64
import select
import socket
import sys
from pathlib import Path

Sip = "127.0.0.1"
Sport = 8080


def abort(msg):
    print("ERROR: " + msg, file=sys.stderr)
    sys.exit(1)


def parse_arguments():
    args = {}

    try:
        args["command"] = sys.argv[1].strip().lower()
    except IndexError:
        abort("Please Provide Command")

    try:
        args["filename"] = sys.argv[2].strip()
    except IndexError:
        abort("include filename")

    if args["command"] == "upload":
        pass
    elif args["command"] == "download":
        pass
    elif args["command"] == "delete":
        pass
    elif args["command"] == "rename":
       
        try:
            args["new_filename"] = sys.argv[3].strip()
        except IndexError:
            abort("Provide new filename")
    else:
        abort("invalid")

    return args


def do_upload(sock, filename):
    file = Path(filename)
    if not file.is_file():
        abort("invalid")
    encoded = base64.b64encode(file.read_bytes()).decode()
    msg = "{}\n{}\n{}".format("Upload", file.name, encoded)
    sock.sendto(msg.encode(), (Sip, Sport))


def do_download(sock, filename):
    msg = "{}\n{}".format("Download", filename)
    sock.sendto(msg.encode(), (Sip, Sport))
    ready = select.select([sock], [], [], 1)[0]
    if ready:
        data = sock.recv(65536)
        Path("download/").mkdir(parents=True, exist_ok=True)
        Path("download/{}".format(filename)).write_bytes(data)
    else:
        abort("timeout")


def do_delete(sock, filename):
    msg = "{}\n{}".format("Delete", filename)
    sock.sendto(msg.encode(), (Sip, Sport))


def do_rename(sock, filename, new_filename):
    msg = "{}\n{}\n{}".format("Rename", filename, new_filename)
    sock.sendto(msg.encode(), (Sip, Sport))


def main():
    args = parse_arguments()
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((Sip, Sport))
    if args["command"] == "upload":
        do_upload(sock, args["filename"])
    elif args["command"] == "download":
        do_download(sock, args["filename"])
    elif args["command"] == "delete":
        do_delete(sock, args["filename"])
    elif args["command"] == "rename":
        do_rename(sock, args["filename"], args["new_filename"])
    sock.close()


if __name__ == "__main__":
    main()
