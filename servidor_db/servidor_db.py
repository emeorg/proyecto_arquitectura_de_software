import socket
import sys
import psycopg2
import time
import os

# --- (La configuración de la DB y la función connect_to_db no cambian) ---

DB_HOST = os.environ.get('DB_HOST', 'db')
DB_NAME = os.environ.get('DB_NAME', 'soabusdb')
DB_USER = os.environ.get('DB_USER', 'admin')
DB_PASS = os.environ.get('DB_PASS', 'admin')

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
            
            if query_str.strip().upper().startswith("SELECT"):
                rows = cur.fetchall()
                if not rows:
                    result_str = "Consulta OK. No se encontraron filas."
                else:
                    result_str = ", ".join([str(row) for row in rows])
            else:
                conn.commit()
                result_str = f"Comando OK. {cur.rowcount} filas afectadas."

        return result_str

    except Exception as e:
        conn.rollback() 
        print(f"Error al ejecutar consulta: {e}")
        return f"Error de consulta: {e}"

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
            print("El bus cerró la conexión (recv 5).")
            break

        amount_expected = int(amount_expected_bytes.decode('utf-8'))

        while amount_received < amount_expected: 
            data = sock.recv(amount_expected - amount_received)
            amount_received += len(data)

        if not data:
            break

        print("Processing command...")
        print('received {!r}'.format(data))

        data_str = data.decode('utf-8')

        if (sinit == 1):
            sinit = 0
            print(f"Registro en el bus confirmado: {data_str}")
        else:
            service_prefix = "serdb" 
            if data_str.startswith(service_prefix):
                query_str = data_str[len(service_prefix):].strip() 
                
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