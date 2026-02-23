import socket
import json
from protocol import CommunicationProtocol

HOST = '127.0.0.1'
PORT = 65432

def send_request(msg_obj):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((HOST, PORT))
            s.sendall(msg_obj.serialize().encode('utf-8'))
            response = s.recv(2048).decode('utf-8')
            return CommunicationProtocol.deserialize(response)
    except ConnectionRefusedError:
        print("Could not connect to the server")
        return None
    
def logged_in_menu(client_id):
    print("\n- Welcome to the Car Sharing App! -")
    while True:
        print("\n1. View Available Cars")
        print("2. Rent a car")
        print("3. End rental")
        print("Q. Logout")

        choice = input("Enter your choice: ")
        
        if choice == '1':
            message = CommunicationProtocol(client_id = client_id, message_id = 1, payload="")
            response = send_request(message)
            if response and response.message_id == 4:
                try:
                    available_cars = json.loads(response.payload)
                    if not available_cars:
                        print("No cars are available at the moment")
                    else:
                        for vin, details in available_cars.items():
                            print(f"VIN: {vin}, Make: {details['make']}, Model: {details['model']}, Year: {details['year']}, Color: {details['color']}, Location: {details['location']}, Price per day: {details['price_per_day']}, Currency: {details['currency']}")
                except json.JSONDecodeError:
                    print("Failed to decode the list of available cars")
            else:
                error = 'Unknown error'
                if response:
                    error = response.payload
                else:
                    error = "Connection error"
                print(f"Failed to obtain the list of available cars: {error}")
        elif choice == '2':
            vin = input("Enter the VIN of the car you want to rent: ")
            message = CommunicationProtocol(client_id = client_id, message_id = 2, payload = vin)
            response = send_request(message)
            if response and response.message_id == 4:
                print("Car rented successfully")
            else:
                error = 'Unknown error'
                if response:
                    error = response.payload
                else:
                    error = "Connection error"
                print(f"Failed to rent the car: {error}")
        elif choice == '3':
            vin = input("Enter the VIN of the car you want to return: ")
            message = CommunicationProtocol(client_id = client_id, message_id = 3, payload = vin)
            response = send_request(message)
            if response and response.message_id == 4:
                print("Car returned successfully")
            else:
                error = 'Unknown error'
                if response:
                    error = response.payload
                else:
                    error = "Connection error"
                print(f"Failed to return the car: {error}")
        elif choice == 'Q' or choice == 'q':
            print("Logging out...")
            payload_data = json.dumps({"client_id": client_id})
            message = CommunicationProtocol(client_id = client_id, message_id = 7, payload = payload_data)
            response = send_request(message)
            if response and response.message_id == 4:
                print("Logout successful")
            else:
                print("Logout failed")
            return

def menu():
    my_client_id = None

    while True:
        print("\nCARSHARING MENU")
        print("1. Create Account")
        print("2. Login")
        print("Q. Quit")
        choice = input("Enter your choice: ")

        if choice == '1':
            username = input("Enter your name: ")
            driver_license = input("Enter your driver license number: ")
            password = input("Enter your password: ")

            payload_data = json.dumps({
                "username": username,
                "driver_license": driver_license,
                "password": password
            })
            message = CommunicationProtocol(client_id = 0, message_id = 0, payload = payload_data)
            response = send_request(message)
            
            if response and response.message_id == 4:
                my_client_id = int(response.payload)
                print(f"Account created. Your client ID is {my_client_id}")
        elif choice == '2':
            try:
                username = input("Enter your username: ")
                password = input("Enter your password: ")

                payload_data = json.dumps({
                    "username": username,
                    "password": password
                })
                message = CommunicationProtocol(client_id = 0, message_id = 6, payload = payload_data)

                response = send_request(message)
                if response and response.message_id == 4:
                    my_client_id = response.client_id
                    print("Login successful")
                    logged_in_menu(my_client_id)
                    my_client_id = None
                else:
                    print("Login failed")
            except ValueError:
                print("Invalid input. Please try again.")
        elif choice == 'Q' or choice == 'q':
            print("Exiting the program")
            return

if __name__ == "__main__":
    menu()
    
