import socket
import sys
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich import box
from rich.text import Text

console = Console()

SERVIDOR_NAME = "servi"
SERVIDOR_LISTA_NAME = "lista"
SERVIDOR_BUSQUEDA_NAME = "buspr"
SERVIDOR_VENTA_NAME = "venta"

def show_header():
    """Muestra el encabezado principal de la aplicación."""
    header = Text("SISTEMA DE GESTION DE VENTAS", style="bold cyan", justify="center")
    console.print(Panel(header, box=box.DOUBLE, border_style="cyan"))

def show_menu():
    """Muestra el menú principal con estilo moderno."""
    table = Table(show_header=False, box=box.ROUNDED, border_style="blue", padding=(0, 2))
    table.add_column("Opcion", style="cyan bold", width=8)
    table.add_column("Descripcion", style="white")
    
    table.add_row("1", "Enviar mensaje personalizado")
    table.add_row("2", "Ver listas disponibles")
    table.add_row("3", "Buscar producto")
    table.add_row("4", "Ver ventas")
    table.add_row("0", "Salir")
    
    console.print("\n")
    console.print(table)

def show_menu_lista():
    """Muestra el submenú de listas."""
    table = Table(title="TIPOS DE LISTA", show_header=False, box=box.ROUNDED, border_style="green")
    table.add_column("Opcion", style="green bold", width=8)
    table.add_column("Descripcion", style="white")
    
    table.add_row("1", "Ver todos los productos")
    table.add_row("2", "Ver todos los clientes")
    table.add_row("0", "Volver al menu principal")
    
    console.print("\n")
    console.print(table)

def show_menu_busqueda():
    """Muestra el submenú de búsqueda."""
    table = Table(title="BUSQUEDA DE PRODUCTOS", show_header=False, box=box.ROUNDED, border_style="yellow")
    table.add_column("Opcion", style="yellow bold", width=8)
    table.add_column("Descripcion", style="white")
    
    table.add_row("1", "Buscar por nombre")
    table.add_row("2", "Buscar por consola")
    table.add_row("0", "Volver al menu principal")
    
    console.print("\n")
    console.print(table)

def show_menu_ventas():
    """Muestra el submenú de ventas."""
    table = Table(title="VER VENTAS", show_header=False, box=box.ROUNDED, border_style="magenta")
    table.add_column("Opcion", style="magenta bold", width=8)
    table.add_column("Descripcion", style="white")
    
    table.add_row("1", "Ventas de este mes")
    table.add_row("2", "Ventas del ultimo mes")
    table.add_row("3", "Ventas de un mes especifico")
    table.add_row("4", "Ventas por rango de tiempo")
    table.add_row("0", "Volver al menu principal")
    
    console.print("\n")
    console.print(table)

def prepare_message(service_name, payload_str):
    """Prepara el mensaje para enviar al bus."""
    full_payload = service_name + payload_str
    full_payload_bytes = full_payload.encode('utf-8')
    length_str = str(len(full_payload_bytes)).zfill(5)
    message_to_send = length_str.encode('utf-8') + full_payload_bytes
    return message_to_send

def call_service(sock, service_name, payload_str):
    """Prepara, envía y recibe un mensaje del bus con feedback visual."""
    try:
        message_to_send = prepare_message(service_name, payload_str)

        console.print(f"\n[bold cyan]>[/bold cyan] Enviando a '[yellow]{service_name}[/yellow]': [white]{payload_str}[/white]")
        sock.sendall(message_to_send)

        with console.status("[bold green]Esperando respuesta del servidor...", spinner="dots"):
            amount_received = 0
            
            amount_expected_bytes = sock.recv(5)
            if not amount_expected_bytes:
                return
                
            amount_expected = int(amount_expected_bytes.decode('utf-8'))

            data = b''
            while amount_received < amount_expected:
                chunk = sock.recv(amount_expected - amount_received) 
                if not chunk:
                    return
                data += chunk
                amount_received += len(chunk)

        console.print("[bold green][OK][/bold green] Respuesta recibida\n")
        
        full_response_str = data.decode('utf-8')

        try:
            left, sep, right = full_response_str.rpartition('_')
            if sep:
                console.print(Panel(right, title="[bold cyan]Respuesta del Servidor[/bold cyan]", 
                                  border_style="green", box=box.ROUNDED))
            else:
                console.print(Panel(full_response_str, title="[bold cyan]Respuesta del Servidor[/bold cyan]", 
                                  border_style="green", box=box.ROUNDED))
        except ValueError:
            console.print(Panel(full_response_str, title="[bold cyan]Respuesta del Servidor[/bold cyan]", 
                              border_style="green", box=box.ROUNDED))

    except socket.error as e:
        console.print(f"[bold red][ERROR][/bold red] Error de socket: {e}")
    except Exception as e:
        console.print(f"[bold red][ERROR][/bold red] Error inesperado: {e}")

def main():
    console.clear()
    show_header()
    
    try:
        with console.status("[bold yellow]Conectando al bus...", spinner="dots"):
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            bus_address = ('soabus', 5000)
            sock.connect(bus_address)
        
        console.print(f"[bold green][OK][/bold green] Conectado a {bus_address[0]}:{bus_address[1]}\n")
    except socket.error as e:
        console.print(f"[bold red][ERROR][/bold red] No se pudo conectar al bus: {e}")
        console.print("[yellow]Asegurate de que 'soabus' este corriendo.[/yellow]")
        sys.exit(1)

    try:
        while True:
            show_menu()
            choice = Prompt.ask("\n[bold cyan]Seleccione una opcion[/bold cyan]", 
                              choices=["0", "1", "2", "3", "4"], 
                              default="0")

            if choice == '1':
                newMessage = Prompt.ask(f"\n[cyan]Ingrese el mensaje a enviar a '{SERVIDOR_NAME}'[/cyan]")
                call_service(sock, SERVIDOR_NAME, newMessage)

            elif choice == '2':
                show_menu_lista()
                choice_lista = Prompt.ask("\n[bold green]Seleccione una opcion[/bold green]", 
                                        choices=["0", "1", "2"], 
                                        default="0")

                if choice_lista == '1':
                    call_service(sock, SERVIDOR_LISTA_NAME, "LISTA_PRODUCTOS")
                elif choice_lista == '2':
                    call_service(sock, SERVIDOR_LISTA_NAME, "LISTA_CLIENTES")

            elif choice == '3':
                show_menu_busqueda()
                choice_busqueda = Prompt.ask("\n[bold yellow]Seleccione una opcion[/bold yellow]", 
                                           choices=["0", "1", "2"], 
                                           default="0")

                if choice_busqueda == '1':
                    nombre_producto = Prompt.ask("\n[cyan]Ingrese el nombre del producto[/cyan]")
                    call_service(sock, SERVIDOR_BUSQUEDA_NAME, f"BUSQUEDA_PRODUCTO_{nombre_producto}")
                elif choice_busqueda == '2':
                    nombre_consola = Prompt.ask("\n[cyan]Ingrese el nombre de la consola[/cyan]")
                    call_service(sock, SERVIDOR_BUSQUEDA_NAME, f"BUSQUEDA_CONSOLA_{nombre_consola}")

            elif choice == '4':
                show_menu_ventas()
                choice_venta = Prompt.ask("\n[bold magenta]Seleccione una opcion[/bold magenta]", 
                                        choices=["0", "1", "2", "3", "4"], 
                                        default="0")

                if choice_venta == '1':
                    call_service(sock, SERVIDOR_VENTA_NAME, "VENTAS_MES_ACTUAL")
                elif choice_venta == '2':
                    call_service(sock, SERVIDOR_VENTA_NAME, "VENTAS_MES_ULTIMO")
                elif choice_venta == '3':
                    mes_seleccionado = Prompt.ask("\n[cyan]Ingrese la fecha (MM-AAAA)[/cyan]")
                    call_service(sock, SERVIDOR_VENTA_NAME, f"VENTAS_MES_ESPECIFICO_{mes_seleccionado}")
                elif choice_venta == '4':
                    rango_inicio = Prompt.ask("\n[cyan]Inicio del rango (MM-AAAA)[/cyan]")
                    rango_fin = Prompt.ask("[cyan]Final del rango (MM-AAAA)[/cyan]")
                    call_service(sock, SERVIDOR_VENTA_NAME, f"VENTAS_MES_RANGO_{rango_inicio}_&_{rango_fin}")

            elif choice == '0':
                if Confirm.ask("\n[yellow]Esta seguro que desea salir?[/yellow]", default=True):
                    break

    finally:
        console.print("[dim]Cerrando conexion del cliente...[/dim]")
        sock.close()

if __name__ == "__main__":
    main()