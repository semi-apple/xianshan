import socket
import json
import sys

class Client:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        
    def send(self, data):
        # convert data to json
        serialized_data = json.dumps(data, ensure_ascii=False).encode('utf-8')
        
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_sock:
            try:
                client_sock.connect((self.host, self.port))
                print("received")

                client_sock.sendall(serialized_data)
                print(f"data sent: {data}")
                
                response = client_sock.recv(1024).decode('utf-8')
                print(f"server response: {response}")
            except Exception as e:
                print(f"error: {e}")
            
            finally:
                sys.exit(0)
            
    