import socket
import threading
import os
import sys
import base64

# Function to decrypt the IP address
def decrypt_ip(encoded_ip):
    return base64.urlsafe_b64decode(encoded_ip.encode()).decode()

# Function to receive messages from the server
def receive_messages(client_socket):
    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8')
            if not message:
                os.system('cls' if os.name == 'nt' else 'clear')
                print("Server has closed the connection.")
                client_socket.close()
                os._exit(0)
            if message == "Server is shutting down.":
                client_socket.close()
                os._exit(0)
            print(f"\n{message}\n")
        except socket.error:
            os.system('cls' if os.name == 'nt' else 'clear')
            print("Disconnected from server.")
            client_socket.close()
            os._exit(0)

# Function to handle client-side commands
def handle_commands(client_socket, message, username):
    if message.startswith('/'):
        if message == '/clear' or message == '/cls':
            os.system('cls' if os.name == 'nt' else 'clear')
            print("")
        elif message == '/help':
            print("Commands:")
            print("/clear or /cls   - Clear the screen")
            print("/help            - Display this help message")
            print("/list            - List all connected users")
            print("/quit            - Leave the chat")
        elif message in ['/list', '/users', '/clients', '/online', '/ls']:
            client_socket.send('/list'.encode('utf-8'))
        elif message == '/quit':
            client_socket.send(f"{username} has left the chat.".encode('utf-8'))
            client_socket.close()
            sys.exit()
        else:
            print('Unknown command - type /help for a list of commands.')
    else:
        client_socket.send(message.encode('utf-8'))

# Main function to start the client
def main():
    encoded_ip = input("Enter the server connection code: ")
    HOST = decrypt_ip(encoded_ip)
    PORT = 5000  # Make sure the port matches the server port

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect((HOST, PORT))
    except socket.error as e:
        print(f"Unable to connect to server: {e}")
        sys.exit()

    # Prompt the user for a username
    username = input("Enter your username: ")
    print("")
    client_socket.send(username.encode('utf-8'))
    os.system('cls' if os.name == 'nt' else 'clear')

    # Start a thread to receive messages from the server
    thread = threading.Thread(target=receive_messages, args=(client_socket,))
    thread.start()

    while True:
        try:
            while True:
                message = input()
                print("")
                handle_commands(client_socket, message, username)
        except KeyboardInterrupt:
            pass

if __name__ == '__main__':
    main()
