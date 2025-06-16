import requests
import json
import os

# Configuración inicial
ROUTER = {
    "host": "192.168.56.101",
    "port": "443",
    "user": "cisco",
    "password": "cisco"
}

HEADERS = {
    "Accept": "application/yang-data+json",
    "Content-Type": "application/yang-data+json"
}

BASE_URL = f"https://{ROUTER['host']}:{ROUTER['port']}/restconf/data"

# Desactiva advertencias de certificado
requests.packages.urllib3.disable_warnings()


def limpiar():
    os.system('cls' if os.name == 'nt' else 'clear')


def ver_interfaces():
    url = f"{BASE_URL}/ietf-interfaces:interfaces"
    response = requests.get(url, auth=(ROUTER["user"], ROUTER["password"]),
                            headers=HEADERS, verify=False)
    
    if response.status_code == 200:
        interfaces = response.json()["ietf-interfaces:interfaces"]["interface"]
        print("\n--- Interfaces ---")
        for intf in interfaces:
            print(f"Nombre: {intf['name']}")
            print(f"  Estado: {'Habilitado' if intf['enabled'] else 'Deshabilitado'}")
            print(f"  Descripción: {intf.get('description', 'Sin descripción')}\n")
    else:
        print("Error al obtener interfaces:", response.status_code, response.text)


def cambiar_descripcion_interfaz():
    interfaz = input("Nombre de la interfaz (ej. GigabitEthernet1): ")
    descripcion = input("Nueva descripción: ")

    url = f"{BASE_URL}/ietf-interfaces:interfaces/interface={interfaz}"
    payload = {
        "ietf-interfaces:interface": {
            "name": interfaz,
            "description": descripcion,
            "type": "iana-if-type:ethernetCsmacd",
            "enabled": True
        }
    }

    response = requests.patch(url, auth=(ROUTER["user"], ROUTER["password"]),
                              headers=HEADERS, data=json.dumps(payload), verify=False)
    
    if response.status_code in [200, 204]:
        print("Descripción actualizada con éxito.")
    else:
        print("Error al actualizar la descripción:", response.status_code, response.text)


def ver_hostname():
    url = f"{BASE_URL}/Cisco-IOS-XE-native:native/hostname"
    response = requests.get(url, auth=(ROUTER["user"], ROUTER["password"]),
                            headers=HEADERS, verify=False)

    if response.status_code == 200:
        hostname = response.json().get("Cisco-IOS-XE-native:hostname", "No disponible")
        print(f"\nHostname del router: {hostname}")
    else:
        print("Error al obtener el hostname:", response.status_code, response.text)


def menu():
    while True:
        limpiar()
        print("=== Herramienta RESTCONF para Router ===")
        print("1. Ver interfaces")
        print("2. Cambiar descripción de interfaz")
        print("3. Ver hostname")
        print("4. Salir")
        opcion = input("Seleccione una opción: ")

        if opcion == "1":
            ver_interfaces()
        elif opcion == "2":
            cambiar_descripcion_interfaz()
        elif opcion == "3":
            ver_hostname()
        elif opcion == "4":
            break
        else:
            print("Opción inválida")

        input("\nPresione Enter para continuar...")


if __name__ == "__main__":
    menu()
