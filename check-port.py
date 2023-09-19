import socket

def find_next_available_port(start_port):
    port = start_port
    while True:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)  # 1 Second Timeout
        result = sock.connect_ex(('127.0.0.1', port))
        sock.close()
        
        if result != 0:  # Port is available
            return port
        port += 1


def find_used_port(start_port):
    port = start_port
    while True:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)  # 1 Second Timeout
        result = sock.connect_ex(('127.0.0.1', port))
        sock.close()
        if result == 0:
            print(f"{port} is used")
        port += 1
        if port == 10050:
            break

if __name__ == "__main__":
    start_port = 10020
    find_used_port(start_port)
    next_available_port = find_next_available_port(start_port)
    print(f"Next available port is {next_available_port}")
