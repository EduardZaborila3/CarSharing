import os
import json
import socket
from protocol import CommunicationProtocol

HOST = '127.0.0.1'
PORT = 65432

SUCCESS = 4
FAILED = 5

USERS_FILE = "users.json"
CARS_FILE = "cars.json"

company_cars = {}

registered_users = {}
logged_in_users = set()
next_client_id = 101

def handle_register(message):
    global next_client_id
    data = json.loads(message.payload)
    
    new_id = next_client_id
    registered_users[new_id] = {
        "username": data["username"],
        "password": data["password"],
        "driver_license": data["driver_license"]
    }
    next_client_id += 1
    save_users()

    print(f"Registered new user: {data['username']} with ID {new_id}")
    return CommunicationProtocol(client_id = new_id, message_id = SUCCESS, payload = str(new_id))

def handle_login(message):
    data = json.loads(message.payload)
    username = data["username"]
    password = data["password"]
    
    load_users()

    client_id = None
    for id, user_data in registered_users.items():
        if user_data["username"] == username and user_data["password"] == password:
            client_id = id
            break

    if client_id is not None:
        logged_in_users.add(client_id)
        print(f"User {username}(ID: {client_id}) logged in")
        return CommunicationProtocol(client_id, SUCCESS, "Login successful")
    else:
        print(f"User with ID {client_id} failed to log in")
        return CommunicationProtocol(client_id, FAILED, "Login failed")
    
def handle_logout(message):
    client_id = message.client_id
    if client_id in logged_in_users:
        logged_in_users.remove(client_id)
        print(f"User with ID {client_id} logged out")
        return CommunicationProtocol(client_id, SUCCESS, "Logout successful")
    else:
        print(f"User with ID {client_id} failed to log out")
        return CommunicationProtocol(client_id, FAILED, "Logout failed")
    
def handle_query_cars(message):
    available_cars = {}
    for vin, details in company_cars.items():
        if details.get("status") == "available":
            available_cars[vin] = details
        
    payload_data = json.dumps(available_cars)

    return CommunicationProtocol(message.client_id, SUCCESS, payload_data)

def handle_start_rental(message):
    vin = message.payload
    if vin in company_cars and company_cars[vin].get("status") == "available":
        company_cars[vin]["status"] = "rented"
        company_cars[vin]["rented_by"] = message.client_id
        save_cars()
        print(f"Car with VIN {vin} has been rented by user with ID {message.client_id}")
        return CommunicationProtocol(message.client_id, SUCCESS, "Rental started")
    else:
        return CommunicationProtocol(message.client_id, FAILED, "Car not available")
    
def handle_end_rental(message):
    vin = message.payload

    if vin in company_cars and company_cars[vin].get("status") == "rented":
        if company_cars[vin]["rented_by"] == message.client_id:
            company_cars[vin]["status"] = "available"
            company_cars[vin]["rented_by"] = None
            save_cars()
            print(f"Client with ID {message.client_id} returned car with VIN {vin}")
            return CommunicationProtocol(message.client_id, SUCCESS, "Rental ended")
        else:
            return CommunicationProtocol(message.client_id, FAILED, "You didnt rent this car")
    else:
        return CommunicationProtocol(message.client_id, FAILED, "Car is not rented")
    
def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen()

    load_users()
    load_cars()

    print(f"Server started on {HOST}:{PORT}")
    while True:
        conn, addr = server_socket.accept()
        with conn:
            data = conn.recv(1024).decode('utf-8')
            if not data:
                continue

            message = CommunicationProtocol.deserialize(data)

            if message:
                if message.message_id == 0:
                    response = handle_register(message)
                elif message.message_id == 1:
                    response = handle_query_cars(message)
                elif message.message_id == 2:
                    response = handle_start_rental(message)
                elif message.message_id == 3:
                    response = handle_end_rental(message)
                elif message.message_id == 6:
                    response = handle_login(message)
                elif message.message_id == 7:
                    response = handle_logout(message)
                else:
                    response = CommunicationProtocol(message.client_id, FAILED, "Unknown command")
                
                conn.sendall(response.serialize().encode('utf-8'))

def load_users():
    global registered_users, next_client_id
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r') as file:
            loaded_users = json.load(file)
            for k, v in loaded_users.items():
                key = int(k)
                registered_users[key] = v
            
            if registered_users:
                next_client_id = max(registered_users.keys()) + 1
        print("[SERVER] Loaded users from file")
    else:
        print("[SERVER] No file containing users found")

def load_cars():
    global company_cars
    if os.path.exists(CARS_FILE):
        with open(CARS_FILE, 'r') as file:
            company_cars = json.load(file)
        print("[SERVER] Loaded cars from file")
    else:
        print("[SERVER] No file containing cars found")

def save_users():
    with open(USERS_FILE, "w") as file:
        json.dump(registered_users, file, indent = 4)

def save_cars():
    with open(CARS_FILE, "w") as file:
        json.dump(company_cars, file, indent=4)

if __name__ == "__main__":
    start_server()