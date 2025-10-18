import socket
import sys

def show_menu():
    """Muestra las opciones del menú al usuario."""
    print("\n--- Menú de Cliente del Bus ---")
    print("1. Enviar mensaje a 'servi'")
    print("2. Ver la lista de productos")
    print("3. [Función Futura (no implementada)]")
    print("0. Salir")

def show_menu_lista():
    """Muestra las opciones del submenú de las listas."""
    print("\n--- Tipos de Lista ---")
    print("1. Ver todos los productos")
    print("2. Ver  todos los clientes")
    print("0. Volver al menú principal")

def prepare_message(service_name, payload_str):
    """Prepara el mensaje para enviar al bus.

    Este formato incluye un prefijo de 5 bytes que indica
    la longitud total del mensaje (nombre del servicio + payload).

    Args:
        service_name (str): Nombre del servicio destino.
        payload_str (str): Mensaje a enviar.
    Returns:
        bytes: Mensaje completo listo para enviar.
    """
    full_payload = service_name + payload_str
    full_payload_bytes = full_payload.encode('utf-8')
    length_str = str(len(full_payload_bytes)).zfill(5)
    message_to_send = length_str.encode('utf-8') + full_payload_bytes
    return message_to_send

def call_service(sock, service_name, payload_str):
    """Prepara, envía y recibe un mensaje del bus.

    Esta función implementa un protocolo de cliente simple:
    1. Envía un mensaje formateado al servicio.
    2. Espera una respuesta.
    3. Lee los primeros 5 bytes para saber la longitud del mensaje.
    4. Lee el resto del mensaje y lo imprime en la consola.

    La función maneja internamente las excepciones de socket
    imprimiendo el error, pero no las propaga.

    Args:
        sock (socket.socket): Socket ya conectado al bus.
        service_name (str): Nombre del servicio destino.
        payload_str (str): Mensaje (payload) a enviar.

    Returns:
        None: La función imprime la respuesta recibida directamente
        en la consola
    """
    try:
        message_to_send = prepare_message(service_name, payload_str)

        print(f"\n[Enviando a '{service_name}']: {payload_str}")
        sock.sendall(message_to_send)

        print("... Esperando respuesta del bus ...")
        amount_received = 0
        amount_expected = int(sock.recv(5))

        data = b''
        while amount_received < amount_expected:
            chunk = sock.recv(amount_expected - amount_received)
            if not chunk:
                print("Error: Conexión cerrada por el servidor.")
                return
            data += chunk
            amount_received += len(chunk)

        print("[Respuesta recibida]")
        print(f"Datos: {data!r} ({data.decode('utf-8')})")

    except socket.error as e:
        print(f"Error de socket: {e}")
    except Exception as e:
        print(f"Ocurrió un error inesperado: {e}")

def main():
    # 1. Conectarse al bus
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        bus_address = ('soabus', 5000)
        print(f"Conectando a {bus_address[0]} en el puerto {bus_address[1]}...")
        sock.connect(bus_address)
        print("¡Conectado!")
    except socket.error as e:
        print(f"No se pudo conectar al bus: {e}")
        print("Asegúrate de que 'soabus' esté corriendo.")
        sys.exit(1)


    # 2. Menú
    try:
        while True:
            show_menu()
            choice = input("Seleccione una opción: ")

            if choice == '1':
                newMessage = input("Ingrese el mensaje a enviar a 'servi': ")
                call_service(sock, "servi", newMessage)

            elif choice == '2':
                show_menu_lista()
                choice_lista = input("Seleccione una opción de lista: ")

                if choice_lista == '1':
                    call_service(sock, "lista", "LISTA_PRODUCTOS")

                elif choice_lista == '2':
                    call_service(sock, "lista", "LISTA_CLIENTES")

                elif choice_lista == '0':
                    continue

            elif choice == '3':
                print("\n[Función aún no implementada]")

            elif choice == '0':
                print("Cerrando conexión... Adiós.")
                break

            else:
                print(f"\n[Error: '{choice}' no es una opción válida. Intente de nuevo.]")

    finally:
        print("Cerrando conexión del cliente.")
        sock.close()

if __name__ == "__main__":
    main()