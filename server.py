import socket
import threading
import sys
import os
import time
import base64

# Server information
HOST = '0.0.0.0'
PORT = 5000

# List to keep track of connected clients and their usernames
clients = []
usernames = {}
threads = []

shutdown = False

# Function to decrypt the IP address
def decrypt_ip(encoded_ip):
    return base64.urlsafe_b64decode(encoded_ip.encode()).decode()

# Function to handle incoming messages from a client
def handle_client(client_socket):
    try:
        # Receive the username from the client
        username = client_socket.recv(1024).decode('utf-8')
        usernames[client_socket] = username
        broadcast(f"{username} has joined the chat.", client_socket)

        while True:
            message = client_socket.recv(1024).decode('utf-8')
            if message == '/list':
                client_list = [user for user in usernames.values()]
                client_socket.send('\n'.join(client_list).encode('utf-8'))
            else:
                broadcast(f"{username}: {message}", client_socket)
    except:
        remove_client(client_socket)

# Function to broadcast messages to all connected clients
def broadcast(message, current_socket=None):
    for client in clients:
        if client != current_socket:
            try:
                client.send(message.encode('utf-8'))
            except:
                remove_client(client)

# Function to remove a client
def remove_client(client_socket):
    if client_socket in clients:
        clients.remove(client_socket)
        username = usernames.pop(client_socket, 'Unknown')
        broadcast(f"{username} has left the chat.")
        try:
            client_socket.close()
        except:
            pass

# Function to close all client connections and stop the server
def shutdown_server(server):
    print("Shutting down server...")
    broadcast("Server is shutting down.")
    for client in clients:
        try:
            client.send("Server is shutting down.".encode('utf-8'))
            client.close()
        except:
            pass
    server.close()

    # Stop all threads except the current one
    current_thread = threading.current_thread()
    for thread in threads:
        if thread is not current_thread:
            thread.join(timeout=1)
    
    shutdown = True
    sys.exit()

# Main function to start the server
def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen(5)
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f'Server started on {HOST}:{PORT}')
    print("")
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)
    print(f'Your IP4 address: {ip_address}')
    print("")

    def listen_for_shutdown_command():
        while True:
            command = input()
            if command == '/shutdown':
                shutdown_server(server)

    # Start a thread to listen for the shutdown command
    shutdown_thread = threading.Thread(target=listen_for_shutdown_command, daemon=True)
    shutdown_thread.start()
    threads.append(shutdown_thread)

    while True:
        try:
            client_socket, client_address = server.accept()
            print(f'Connection from {client_address}')
            clients.append(client_socket)
            client_thread = threading.Thread(target=handle_client, args=(client_socket,))
            client_thread.start()
            threads.append(client_thread)
        except KeyboardInterrupt:
            shutdown_server(server)
        except:
            shutdown_server(server)
            break
    time.sleep(2)
    server.close()
    sys.exit()

if __name__ == '__main__':
    main()
