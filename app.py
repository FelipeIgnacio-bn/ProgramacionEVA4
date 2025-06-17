import requests
import json
import os

# Configuración inicial
ROUTER = {
    "host": "192.168.56.101",
    "port": "443",
    "user": "cisco",
    "password": "cisco123!"
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


def agregar_loopback():
    interfaz = input("Nombre de la interfaz Loopback (ej. Loopback100): ")
    ip = input("Dirección IP (ej. 10.1.1.1): ")
    mascara = input("Máscara de subred (ej. 255.255.255.0): ")

    url = f"{BASE_URL}/ietf-interfaces:interfaces/interface={interfaz}"
    payload = {
        "ietf-interfaces:interface": {
            "name": interfaz,
            "description": "Interfaz Loopback creada por RESTCONF",
            "type": "iana-if-type:softwareLoopback",
            "enabled": True,
            "ietf-ip:ipv4": {
                "address": [
                    {
                        "ip": ip,
                        "netmask": mascara
                    }
                ]
            }
        }
    }

    response = requests.put(url, auth=(ROUTER["user"], ROUTER["password"]),
                            headers=HEADERS, data=json.dumps(payload), verify=False)

    if response.status_code in [200, 201, 204]:
        print(f"Loopback {interfaz} creada con éxito.")
    else:
        print("Error al crear la interfaz Loopback:", response.status_code, response.text)

def eliminar_loopback():
    interfaz = input("Nombre de la interfaz Loopback a eliminar (ej. Loopback100): ")

    url = f"{BASE_URL}/ietf-interfaces:interfaces/interface={interfaz}"

    response = requests.delete(url, auth=(ROUTER["user"], ROUTER["password"]),
                               headers=HEADERS, verify=False)

    if response.status_code in [200, 204]:
        print(f"Loopback {interfaz} eliminada con éxito.")
    else:
        print("Error al eliminar la interfaz Loopback:", response.status_code, response.text)



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
        print("3. Crear interfaz loopback")
        print("4. Eliminar interfaz loopback")
        print("5. Ver hostname")
        print("6. Salir")
        opcion = input("Seleccione una opción: ")

        if opcion == "1":
            ver_interfaces()
        elif opcion == "2":
            cambiar_descripcion_interfaz()
        elif opcion == "3":
            agregar_loopback()
        elif opcion == "4":
            eliminar_loopback()
        elif opcion == "5":
            ver_hostname()
        elif opcion == "6"
            break
        else:
            print("Opción inválida")

        input("\nPresione Enter para continuar...")


if __name__ == "__main__":
    menu()
