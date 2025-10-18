import socket
import sys
import psycopg2
import time
import os

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

def get_productos(conn):
    """
    Ejecuta la consulta 'SELECT nombre FROM productos' y devuelve un string.
    """
    if not conn:
        return "Error: Sin conexión a la DB"
        
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT nombre FROM productos;")
            # fetchall() devuelve una lista de tuplas: [('ProductoA',), ('ProductoB',)]
            rows = cur.fetchall()
            
            # Convertimos la lista de tuplas en un string simple
            # [row[0] for row in rows] -> ['ProductoA', 'ProductoB']
            # ", ".join(...) -> "ProductoA, ProductoB"
            if not rows:
                return "No hay productos en la base de datos."
            
            product_names = ", ".join([row[0] for row in rows])
            return product_names

    except Exception as e:
        print(f"Error al consultar productos: {e}")
        conn.close()
        conn = connect_to_db()
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

# --- Programa Principal ---
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
        amount_expected = int(sock.recv(5))
        
        while amount_received < amount_expected: 
            data = sock.recv(amount_expected - amount_received)
            amount_received += len(data)

        print("Processing command...")
        print('received {!r}'.format(data))

        data_str = data.decode('utf-8')

        if (sinit == 1):
            sinit = 0
            print(f"Registro en el bus confirmado: {data_str}")
        else:
            if data_str.endswith('LISTAR_PRODUCTOS'):
                print("Comando 'LISTAR_PRODUCTOS' recibido.")
                # Llama a la función de la DB
                productos_str = get_productos(db_conn)
                # Envía la respuesta
                send_response(sock, productos_str)
            else:
                print(f"Comando desconocido: {data_str}")
                send_response(sock, "Error: Comando no reconocido")

finally:
    print("Cerrando conexión con la DB y el bus.")
    if db_conn:
        db_conn.close()
    sock.close()