import requests
from requests.auth import HTTPBasicAuth
import json
import os

# Configuración inicial
ROUTERS = {
    "router1": {
        "host": "192.168.3.232",
        "port": "443",
        "user": "cisco",
        "password": "cisco123!",
        "capa": distribucion"
    },
    "router2": {
        "host": "192.168.56.102",
        "port": "443",
        "user": "cisco",
        "password": "cisco123!",
        "capa": "distribucion"
    }
}

HEADERS = {
    "Accept": "application/yang-data+json",
    "Content-Type": "application/yang-data+json"
}

BASE_URL = None  # BASE_URL will be dynamically set based on the selected router

# Desactiva advertencias de certificado
requests.packages.urllib3.disable_warnings()

def limpiar():
    os.system('cls' if os.name == 'nt' else 'clear')

def seleccionar_router():
    print("Seleccione el router:")
    for idx, nombre in enumerate(ROUTERS.keys(), 1):
        print(f"{idx}. {nombre}. {capa}")
    opcion = input("Opción: ")
    nombres = list(ROUTERS.keys())
    if opcion in ["1", "2"]:
        return ROUTERS[nombres[int(opcion)-1]]
    else:
        print("Selección inválida. Usando router1 por defecto.")
        return ROUTERS["router1"]

def ver_interfaces(router):
    base_url = f"https://{router['host']}:{router['port']}/restconf/data"
    url = f"{base_url}/ietf-interfaces:interfaces"
    response = requests.get(url, auth=(router["user"], router["password"]),
                            headers=HEADERS, verify=False)
    # Verifica si la respuesta es exitosa
    if response.status_code == 200:
        interfaces = response.json()["ietf-interfaces:interfaces"]["interface"]
        print("\n--- Interfaces ---")
        for intf in interfaces:
            print(f"Nombre: {intf['name']}")
            print(f"  Estado: {'Habilitado' if intf['enabled'] else 'Deshabilitado'}")
            print(f"  Descripción: {intf.get('description', 'Sin descripción')}\n")
    else:
        print("Error al obtener interfaces:", response.status_code, response.text)

def cambiar_descripcion_interfaz(router):
    interfaz = input("Nombre de la interfaz (ej. GigabitEthernet1): ")
    descripcion = input("Nueva descripción: ")

    base_url = f"https://{router['host']}:{router['port']}/restconf/data"
    url = f"{base_url}/ietf-interfaces:interfaces/interface={interfaz}"
    payload = {
        "ietf-interfaces:interface": {
            "name": interfaz,
            "description": descripcion,
            "type": "iana-if-type:ethernetCsmacd",
            "enabled": True
        }
    }

    response = requests.patch(url, auth=(router["user"], router["password"]),
                              headers=HEADERS, data=json.dumps(payload), verify=False)
    
    if response.status_code in [200, 204]:
        print("Descripción actualizada con éxito.")
    else:
        print("Error al actualizar la descripción:", response.status_code, response.text)

def agregar_loopback(router):
    interfaz = input("Nombre de la interfaz Loopback (ej. Loopback100): ")
    ip = input("Dirección IP (ej. 10.1.1.1): ")
    mascara = input("Máscara de subred (ej. 255.255.255.0): ")

    base_url = f"https://{router['host']}:{router['port']}/restconf/data"
    url = f"{base_url}/ietf-interfaces:interfaces/interface={interfaz}"
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

    response = requests.put(url, auth=(router["user"], router["password"]),
                            headers=HEADERS, data=json.dumps(payload), verify=False)

    if response.status_code in [200, 201, 204]:
        print(f"Loopback {interfaz} creada con éxito.")
    else:
        print("Error al crear la interfaz Loopback:", response.status_code, response.text)

def eliminar_loopback(router):
    interfaz = input("Nombre de la interfaz Loopback a eliminar (ej. Loopback100): ")

    base_url = f"https://{router['host']}:{router['port']}/restconf/data"
    url = f"{base_url}/ietf-interfaces:interfaces/interface={interfaz}"

    
    response = requests.delete(url, auth=(router["user"], router["password"]),
                               headers=HEADERS, verify=False)

    if response.status_code in [200, 204]:
        print(f"Loopback {interfaz} eliminada con éxito.")
    else:
        print("Error al eliminar la interfaz Loopback:", response.status_code, response.text)

def ver_hostname(router):
    base_url = f"https://{router['host']}:{router['port']}/restconf/data"
    url = f"{base_url}/Cisco-IOS-XE-native:native/hostname"
    response = requests.get(url, auth=(router["user"], router["password"]),
                            headers=HEADERS, verify=False)
    if response.status_code == 200:
        hostname = response.json().get("Cisco-IOS-XE-native:hostname", "No disponible")
        print(f"\nHostname del router: {hostname}")
    else:
        print("Error al obtener el hostname:", response.status_code, response.text)

def cambiar_hostname(router_ip, usuario, password, nuevo_hostname):
    url = f"https://{router_ip}/restconf/data/Cisco-IOS-XE-native:native/hostname"
    headers = {
        "Content-Type": "application/yang-data+json",
        "Accept": "application/yang-data+json"
    }
    payload = {
        "Cisco-IOS-XE-native:hostname": nuevo_hostname
    }

    response = requests.put(
        url,
        json=payload,
        headers=headers,
        auth=HTTPBasicAuth(usuario, password),
        verify=False
    )

    if response.status_code in [200, 204]:
        print("Hostname cambiado correctamente.")
    else:
        print(f"Error al cambiar hostname: {response.status_code}\n{response.text}")

def ver_rutas(router):
    base_url = f"https://{router['host']}:{router['port']}/restconf/data"
    url = f"{base_url}/ietf-routing:routing"
    response = requests.get(url, auth=(router["user"], router["password"]),
                            headers=HEADERS, verify=False)

    if response.status_code == 200:
        rutas = response.json().get("ietf-routing:routing", {}).get("routing-instance", [])
        print("\n--- Rutas ---")
        for instancia in rutas:
            if "routing-protocols" in instancia:
                for protocolo in instancia["routing-protocols"]["routing-protocol"]:
                    if "static-routes" in protocolo:
                        for ruta in protocolo["static-routes"]["ipv4"]["route"]:
                            destino = ruta["destination-prefix"]
                            next_hop = ruta["next-hop"]["next-hop-address"]
                            print(f"Destino: {destino}, Next-hop: {next_hop}")
    else:
        print("Error al obtener las rutas:", response.status_code, response.text)

def menu():
    router = seleccionar_router()
    while True:
        limpiar()
        print("=== Herramienta RESTCONF para Router ===")
        print("Router seleccionado:", router['host'])
        print("1. Ver interfaces")
        print("2. Cambiar descripción de interfaz")
        print("3. Crear interfaz loopback")
        print("4. Eliminar interfaz loopback")
        print("5. Ver hostname")
        print("6. Cambiar de router")
        print("7. Cambiar Hostname")
        print("8. Ver rutas")
        print("9. Salir")
        opcion = input("Seleccione una opción: ")
        if opcion == "1":
            ver_interfaces(router)
        elif opcion == "2":
            cambiar_descripcion_interfaz(router)
        elif opcion == "3":
            agregar_loopback(router)
        elif opcion == "4":
            eliminar_loopback(router)
        elif opcion == "5":
            ver_hostname(router)
        elif opcion == "6":
            router = seleccionar_router()
        elif opcion == "7":
            nuevo_hostname = input("Introduce el nuevo hostname para el router: ")
            cambiar_hostname(router['host'], router['user'], router['password'], nuevo_hostname)
        elif opcion == "8":
            ver_rutas(router)
        elif opcion == "9":
            print("Saliendo...")
            break
        else:
            print("Opción inválida")
        input("\nPresione Enter para continuar...")

if __name__ == "__main__":
    menu()
