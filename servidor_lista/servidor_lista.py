import socket
import sys

BUS_ADDRESS = ('soabus', 5000)
MY_SERVICE_NAME = "lista"
DB_SERVICE_NAME = "serdb"

def send_response(sock, payload_str):
    """
    Codifica y envía una respuesta al cliente original 
    en el socket principal.
    """
    response_payload = f"{MY_SERVICE_NAME}OK_{payload_str}"
    
    response_bytes = response_payload.encode('utf-8')
    length_str = str(len(response_bytes)).zfill(5).encode('utf-8')
    message = length_str + response_bytes
    
    print(f"Enviando respuesta: {response_payload}")
    sock.sendall(message)

# --- Función Helper 2: Llamar a otro Servicio (como Cliente) ---
def call_db_service(sql_query):
    """
    Abre una NUEVA conexión al bus para llamar al servicio de DB.
    Actúa como un cliente temporal.
    """
    print(f"Llamando al servicio de DB con consulta: {sql_query}")
    db_sock = None
    try:
        # 1. Preparar el mensaje para servidor_db
        payload = DB_SERVICE_NAME + sql_query
        payload_bytes = payload.encode('utf-8')
        length_str = str(len(payload_bytes)).zfill(5).encode('utf-8')
        message = length_str + payload_bytes

        # 2. Conectar, enviar y recibir
        db_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        db_sock.connect(BUS_ADDRESS)
        db_sock.sendall(message)

        # 3. Recibir la respuesta de servidor_db
        amount_received = 0
        amount_expected_bytes = db_sock.recv(5)
        if not amount_expected_bytes:
            return "Error: No hubo respuesta del servicio de DB"

        amount_expected = int(amount_expected_bytes.decode('utf-8'))

        while amount_received < amount_expected:
            data = db_sock.recv(amount_expected - amount_received)
            amount_received += len(data)

        # 4. Decodificar y limpiar la respuesta
        full_response_str = data.decode('utf-8')

        data_part = full_response_str.split("_", 1)[-1]

        return data_part

    except Exception as e:
        print(f"Error al llamar a call_db_service: {e}")
        return f"Error interno: {e}"
    finally:
        if db_sock:
            db_sock.close()


# --- Programa Principal ---
server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    print(f"Conectando al bus en {BUS_ADDRESS}...")
    server_sock.connect(BUS_ADDRESS)

    # 1. Registrar este servicio
    message = b'00010sinitlista'
    server_sock.sendall(message)
    sinit = 1
    print("Servicio 'lista' registrado, esperando confirmación...")

    # 2. Bucle principal de escucha (como Servidor)
    while True:
        print("\nWaiting for transaction from a client...")
        amount_received = 0

        amount_expected_bytes = server_sock.recv(5)
        if not amount_expected_bytes:
            print("El bus cerró la conexión (recv 5).")
            break

        amount_expected = int(amount_expected_bytes.decode('utf-8'))

        while amount_received < amount_expected:
            data = server_sock.recv(amount_expected - amount_received)
            amount_received += len(data)

        if not data:
            break

        print(f"Processing command... received: {data!r}")
        data_str = data.decode('utf-8')

        if (sinit == 1):
            sinit = 0
            print(f"Registro en el bus confirmado: {data_str}")
        else:
            try:
                command = data_str[len(MY_SERVICE_NAME):].strip()
                
                if command == 'LISTA_PRODUCTOS':
                    print("Comando 'LISTA_PRODUCTOS' recibido.")
                    sql_query = "SELECT nombre FROM productos;"
                    db_result = call_db_service(sql_query)
                    send_response(server_sock, db_result)

                elif command == 'LISTA_CLIENTES':
                    print("Comando 'LISTA_CLIENTES' recibido.")
                    sql_query = "SELECT nombre FROM clientes;"
                    db_result = call_db_service(sql_query)
                    send_response(server_sock, db_result)
                    
                else:
                    print(f"Comando desconocido: {command}")
                    send_response(server_sock, "Error: Comando no reconocido")
            
            except Exception as e:
                print(f"Error procesando el comando: {e}")
                send_response(server_sock, f"Error: {e}")

finally:
    print("Cerrando conexión con el bus.")
    server_sock.close()