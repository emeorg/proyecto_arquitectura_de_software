import socket
import sys

BUS_ADDRESS = ('soabus', 5000)
MY_SERVICE_NAME = "venta"
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

        data_part = full_response_str.split("_", 2)[-1]

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
                
                if command == 'VENTAS_MES_ACTUAL':
                    sql_query_details = """
                        SELECT V.VentaID, V.FechaVenta, C.Nombre || ' ' || C.Apellido AS Cliente, J.Titulo AS Juego, P.Formato, P.Condicion, DV.Cantidad, DV.PrecioUnitarioVenta, V.TotalVenta
                        FROM Ventas AS V
                        JOIN Clientes AS C ON V.ClienteID = C.ClienteID
                        JOIN DetalleVenta AS DV ON V.VentaID = DV.VentaID
                        JOIN Productos AS P ON DV.ProductoID = P.ProductoID
                        JOIN Juegos AS J ON P.JuegoID = J.JuegoID
                        WHERE DATE_TRUNC('month', V.FechaVenta) = DATE_TRUNC('month', NOW())
                        ORDER BY V.FechaVenta;
                    """
                    
                    sql_query_total = """
                        SELECT 'Total de ventas: ' || SUM(V.TotalVenta)
                        FROM Ventas AS V
                        WHERE DATE_TRUNC('month', V.FechaVenta) = DATE_TRUNC('month', NOW());
                    """

                    db_result_details = call_db_service(sql_query_details)
                    db_result_total = call_db_service(sql_query_total)
                    
                    combined_result = db_result_details + "\n\n" + db_result_total
                    
                    send_response(sock, combined_result)

                elif command == 'VENTAS_MES_ULTIMO':
                    sql_query_details = """
                        SELECT V.VentaID, V.FechaVenta, C.Nombre || ' ' || C.Apellido AS Cliente, J.Titulo AS Juego, P.Formato, P.Condicion, DV.Cantidad, DV.PrecioUnitarioVenta, V.TotalVenta
                        FROM Ventas AS V
                        JOIN Clientes AS C ON V.ClienteID = C.ClienteID
                        JOIN DetalleVenta AS DV ON V.VentaID = DV.VentaID
                        JOIN Productos AS P ON DV.ProductoID = P.ProductoID
                        JOIN Juegos AS J ON P.JuegoID = J.JuegoID
                        WHERE DATE_TRUNC('month', V.FechaVenta) = DATE_TRUNC('month', NOW() - interval '1 month')
                        ORDER BY V.FechaVenta;
                    """
                    
                    sql_query_total = """
                        SELECT 'Total de ventas: ' || SUM(V.TotalVenta)
                        FROM Ventas AS V
                        WHERE DATE_TRUNC('month', V.FechaVenta) = DATE_TRUNC('month', NOW() - interval '1 month');
                    """

                    db_result_details = call_db_service(sql_query_details)
                    db_result_total = call_db_service(sql_query_total)
                    
                    combined_result = db_result_details + "\n\n" + db_result_total
                    
                    send_response(sock, combined_result)
                
                elif command.startswith('VENTAS_MES_ESPECIFICO'):
                    mes_ano_str = command.replace('VENTAS_MES_ESPECIFICO_', '')
                    
                    fecha_sql_str = f"01-{mes_ano_str}"

                    where_clause = f"WHERE DATE_TRUNC('month', V.FechaVenta) = DATE_TRUNC('month', TO_DATE('{fecha_sql_str}', 'DD-MM-YYYY'))"
                    
                    sql_query_details = f"SELECT V.VentaID, V.FechaVenta, C.Nombre || ' ' || C.Apellido AS Cliente, J.Titulo AS Juego, P.Formato, P.Condicion, DV.Cantidad, DV.PrecioUnitarioVenta, V.TotalVenta FROM Ventas AS V JOIN Clientes AS C ON V.ClienteID = C.ClienteID JOIN DetalleVenta AS DV ON V.VentaID = DV.VentaID JOIN Productos AS P ON DV.ProductoID = P.ProductoID JOIN Juegos AS J ON P.JuegoID = J.JuegoID {where_clause} ORDER BY V.FechaVenta;"

                    sql_query_total = f"SELECT 'Total de ventas ({mes_ano_str}): ' || SUM(V.TotalVenta) FROM Ventas AS V {where_clause};"

                    db_result_details = call_db_service(sql_query_details)
                    db_result_total = call_db_service(sql_query_total)
                    
                    if not db_result_details:
                        db_result_details = f"No se encontraron ventas para {mes_ano_str}."

                    combined_result = db_result_details + "\n\n" + db_result_total
                    send_response(sock, combined_result)

                elif command.startswith('VENTAS_MES_RANGO_'):
                    rangos_str = command.replace('VENTAS_MES_RANGO_', '')
                    
                    try:
                        rango_inicio_str, rango_fin_str = rangos_str.split('_&_')
                    except ValueError:
                        send_response(sock, "Error: Formato de rango invalido. Use MM-AAAA_&_MM-AAAA")
                        continue

                    fecha_sql_inicio = f"01-{rango_inicio_str}"
                    fecha_sql_fin = f"01-{rango_fin_str}"

                    where_clause_rango = f"WHERE DATE_TRUNC('month', V.FechaVenta) >= DATE_TRUNC('month', TO_DATE('{fecha_sql_inicio}', 'DD-MM-YYYY')) AND DATE_TRUNC('month', V.FechaVenta) <= DATE_TRUNC('month', TO_DATE('{fecha_sql_fin}', 'DD-MM-YYYY'))"
                    
                    sql_query_details = f"SELECT V.VentaID, V.FechaVenta, C.Nombre || ' ' || C.Apellido AS Cliente, J.Titulo AS Juego, P.Formato, P.Condicion, DV.Cantidad, DV.PrecioUnitarioVenta, V.TotalVenta FROM Ventas AS V JOIN Clientes AS C ON V.ClienteID = C.ClienteID JOIN DetalleVenta AS DV ON V.VentaID = DV.VentaID JOIN Productos AS P ON DV.ProductoID = P.ProductoID JOIN Juegos AS J ON P.JuegoID = J.JuegoID {where_clause_rango} ORDER BY V.FechaVenta;"
                    sql_query_total = f"SELECT 'Total de ventas ({rango_inicio_str} a {rango_fin_str}): ' || SUM(V.TotalVenta) FROM Ventas AS V {where_clause_rango};"

                    db_result_details = call_db_service(sql_query_details)
                    db_result_total = call_db_service(sql_query_total)
                    
                    if not db_result_details:
                        db_result_details = f"No se encontraron ventas entre {rango_inicio_str} y {rango_fin_str}."

                    combined_result = db_result_details + "\n\n" + db_result_total
                    send_response(sock, combined_result)

                else:
                    print(f"Comando desconocido: {command}")
                    send_response(sock, "Error: Comando no reconocido")
            
            except Exception as e:
                print(f"Error procesando el comando: {e}")
                send_response(sock, f"Error: {e}")

finally:
    print("Cerrando conexión con el bus.")
    sock.close()