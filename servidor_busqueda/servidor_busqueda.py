import socket
import sys

BUS_ADDRESS = ('soabus', 5000)
MY_SERVICE_NAME = "buspr"
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
        payload = DB_SERVICE_NAME + sql_query
        payload_bytes = payload.encode('utf-8')
        length_str = str(len(payload_bytes)).zfill(5).encode('utf-8')
        message = length_str + payload_bytes

        db_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        db_sock.connect(BUS_ADDRESS)
        db_sock.sendall(message)

        amount_received = 0
        amount_expected_bytes = db_sock.recv(5)
        if not amount_expected_bytes:
            return "Error: No hubo respuesta del servicio de DB"

        amount_expected = int(amount_expected_bytes.decode('utf-8'))

        data = b''
        while amount_received < amount_expected:
            chunk = db_sock.recv(amount_expected - amount_received)
            if not chunk:
                break
            data += chunk
            amount_received += len(chunk)

        full_response_str = data.decode('utf-8')

        data_part = full_response_str.split("_", 1)[-1]

        return data_part

    except Exception as e:
        print(f"Error al llamar a call_db_service: {e}")
        return f"Error interno: {e}"
    finally:
        if db_sock:
            db_sock.close()


sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    print(f"Conectando al bus en {BUS_ADDRESS}...")
    sock.connect(BUS_ADDRESS)

    message = b'00010sinit' + MY_SERVICE_NAME.encode('utf-8')
    sock.sendall(message)
    sinit = 1
    print(f"Servicio '{MY_SERVICE_NAME}' registrado, esperando confirmación...")

    while True:
        print("\nWaiting for transaction from a client...")
        amount_received = 0

        amount_expected_bytes = sock.recv(5)
        if not amount_expected_bytes:
            break
        amount_expected = int(amount_expected_bytes.decode('utf-8'))
        
        data = b''
        while amount_received < amount_expected:
            chunk = sock.recv(amount_expected - amount_received) 
            if not chunk:
                break

            data += chunk
            amount_received += len(chunk)

        data_str = data.decode('utf-8')

        if (sinit == 1):
            sinit = 0
            print(f"Registro en el bus confirmado: {data_str}")
        else:
            try:
                command = data_str[len(MY_SERVICE_NAME):].strip()

                COMMAND_PREFIX = 'BUSQUEDA_PRODUCTO_'
                
                if command.startswith(COMMAND_PREFIX):
                    
                    search_term = command[len(COMMAND_PREFIX):].strip()
                    
                    print(f"Comando 'BUSQUEDA_PRODUCTO' recibido. Término: '{search_term}'")

                    safe_search_term = search_term.replace("'", "''")

                    sql_query = f"""
                        SELECT j.Titulo, c.Nombre, p.Formato, p.Condicion, p.PrecioVenta, p.Stock 
                        FROM Productos AS p 
                        JOIN Juegos AS j ON p.JuegoID = j.JuegoID 
                        JOIN Consolas AS c ON p.ConsolaID = c.ConsolaID 
                        WHERE j.Titulo ILIKE '%{safe_search_term}%';
                    """

                    db_result = call_db_service(sql_query)
                    send_response(sock, db_result)

                else:
                    print(f"Comando desconocido: {command}")
                    send_response(sock, "Error: Comando no reconocido")
            
            except Exception as e:
                print(f"Error procesando el comando: {e}")
                send_response(sock, f"Error: {e}")

finally:
    print("Cerrando conexión con el bus.")
    sock.close()