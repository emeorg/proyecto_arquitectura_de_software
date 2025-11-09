import socket
import sys
import psycopg2
import time
import os

DB_HOST = os.environ.get('DB_HOST')
DB_NAME = os.environ.get('DB_NAME')
DB_USER = os.environ.get('DB_USER')
DB_PASS = os.environ.get('DB_PASS')

def connect_to_db():
    """
    Intenta conectarse a la DB con reintentos.
    Esto es vital porque el script puede iniciar antes que la DB.
    """
    conn = None
    retries = 10
    while retries > 0:
        try:
            conn = psycopg2.connect(
                host=DB_HOST,
                dbname=DB_NAME,
                user=DB_USER,
                password=DB_PASS
            )
            print("Conectado a la base de datos PostgreSQL")
            return conn
        except psycopg2.OperationalError as e:
            print(f"Error conectando a la DB: {e}")
            print(f"Reintentando en 5 segundos... ({retries} intentos restantes)")
            retries -= 1
            time.sleep(5)

    print("No se pudo conectar a la base de datos después de varios intentos.")
    return None

def run_query(conn, query_str):
    """
    Ejecuta una consulta SQL genérica y devuelve el resultado como string.
    ¡¡ADVERTENCIA: VULNERABLE A INYECCIÓN SQL!!
    """
    if not conn:
        return "Error: Sin conexión a la DB"
        
    result_str = ""
    try:
        with conn.cursor() as cur:
            cur.execute(query_str)
            
            if cur.description:
                rows = cur.fetchall()
                
                if not rows:
                    result_str = "OK_No se encontraron resultados"
                else:
                    csv_rows = []
                    for row in rows:
                        str_row = [str(item).strip() for item in row] 
                        csv_rows.append(",".join(str_row))
                        
                    result_str = "OK_" + "\n".join(csv_rows)

            else:
                conn.commit()
                status_message = cur.statusmessage
                result_str = f"OK_{status_message}"

    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Error ejecutando consulta: {error}")
        result_str = f"Error: {error}"
        if conn:
            conn.rollback() # Revertir cambios si algo falló
            
    return result_str

def send_response(sock, payload_str):
    """Codifica y envía una respuesta al bus.
    Args:
        sock (socket.socket): Socket conectado al bus.
        payload_str (str): Mensaje (payload) a enviar.
    Returns:
        None
    """
    response_payload = "serdbOK_" + payload_str
    
    response_bytes = response_payload.encode('utf-8')
    length_str = str(len(response_bytes)).zfill(5).encode('utf-8')
    message = length_str + response_bytes
    
    print(f"Enviando respuesta: {response_payload}")
    sock.sendall(message)

db_conn = connect_to_db()
if not db_conn:
    sys.exit(1)

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
bus_address = ('soabus', 5000)
sock.connect(bus_address)

try:
    message = b'00010sinitserdb'
    sock.sendall(message)
    sinit = 1

    while True:
        print("\nWaiting for transaction")
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

        if not data:
            break
        
        data_str = data.decode('utf-8')

        if (sinit == 1):
            sinit = 0
            print(f"Registro en el bus confirmado: {data_str}")
        else:
            service_prefix = "serdb" 
            if data_str.startswith(service_prefix):
                query_str = data_str[len(service_prefix):].strip()

                if "drop" in query_str.lower() or "delete" in query_str.lower():
                    print("Comando no permitido.")
                    send_response(sock, "Error: Comando no permitido")
                    continue

                if not query_str:
                    print("Comando recibido pero sin consulta.")
                    send_response(sock, "Error: Consulta vacía")
                else:
                    print(f"Comando de consulta recibido: '{query_str}'")
                    result_str = run_query(db_conn, query_str)
                    send_response(sock, result_str)
            else:
                print(f"Comando desconocido (sin prefijo 'serdb'): {data_str}")
                send_response(sock, "Error: Comando no reconocido")

finally:
    print("Cerrando conexión con la DB y el bus.")
    if db_conn:
        db_conn.close()
    sock.close()