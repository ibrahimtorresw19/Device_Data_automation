import csv
import os
from netmiko import ConnectHandler
from netmiko.exceptions import NetmikoAuthenticationException, NetmikoTimeoutException
from tabulate import tabulate

ips_dispositivos = [
    "10.10.20.171",  # R1
    "10.10.20.172",  # R2
    "10.10.20.173",  # SW1
    "10.10.20.174",  # SW2
]

usuario = "cisco"
password = "cisco"
secret = "cisco"

carpeta_destino = os.path.join("..", "Reportes")
os.makedirs(carpeta_destino, exist_ok=True)

ruta_archivo_txt = os.path.join(carpeta_destino, "reporte_inventario.txt")
ruta_archivo_csv = os.path.join(carpeta_destino, "reporte_inventario.csv")

Header = ["Interfaz", "Descripción", "IP", "MAC Address", "Status (Fisico)", "Protocolo (logico)"]
Header_csv = [
    "Equipo",
    "IP Base",
    "IOS",
    "Interfaz",
    "Descripción",
    "IP",
    "MAC Address",
    "Status (Fisico)",
    "Protocolo (logico)",
]

lineas_archivo_txt = []
lineas_archivo_csv = []

for ip in ips_dispositivos:
    dispositivo = {
        "device_type": "cisco_ios",
        "host": ip,
        "username": usuario,
        "password": password,
        "secret": secret,
        "port": 22,
    }

    try:
        with ConnectHandler(**dispositivo) as connect:
            connect.enable()

            nombre_equipo = connect.find_prompt().replace("#", "").replace(">", "").strip()
            print(f"\nNombre obtenido exitosamente. Nombre: {nombre_equipo} ({ip})")

            version = connect.send_command("sh version", use_textfsm=True)
            if isinstance(version, list) and len(version) > 0:
                version_ios = version[0].get("version", "No encontrado")
                software_ios = version[0].get("software_image", "No encontrada")
            else:
                version_ios = "No encontrada (Error de parsing)"
                software_ios = "No encontrada (Error de parsing)"

            encabezado = "\n" + "=" * 90 + "\n"
            encabezado += f"Dispositivo: {nombre_equipo}   |  IP BASE: {ip}    |   IOS: {version_ios}\n"
            encabezado += "=" * 90 + "\n"

            print(f"--- Extrayendo datos de: {nombre_equipo} (IOS: {version_ios} | Software: {software_ios}) ---\n")

            interfaces_raw = connect.send_command("sh interface", use_textfsm=True)
            tabla_interfaces_equipo = []

            if isinstance(interfaces_raw, list):
                for datos in interfaces_raw:
                    interfaz = datos.get("interface", "N/A")
                    description = datos.get("description", "N/A")
                    direccion_ip = datos.get("ip_address", "Sin IP")
                    mac_address = datos.get("mac_address", "Sin MAC")
                    status_fisico = datos.get("link_status", "Desconocido")
                    protocol_logico = datos.get("protocol_status", "Desconocido")

                    tabla_interfaces_equipo.append([
                        interfaz,
                        description,
                        direccion_ip,
                        mac_address,
                        status_fisico,
                        protocol_logico,
                    ])

                    lineas_archivo_csv.append([
                        nombre_equipo,
                        ip,
                        version_ios,
                        interfaz,
                        description,
                        direccion_ip,
                        mac_address,
                        status_fisico,
                        protocol_logico,
                    ])

                tabla_final = tabulate(tabla_interfaces_equipo, headers=Header, tablefmt="grid")
                print(encabezado)
                print(tabla_final)

                lineas_archivo_txt.append(encabezado)
                lineas_archivo_txt.append(tabla_final + "\n")
            else:
                print(f"⚠️ No se pudieron analizar las interfaces con TextFSM en {ip}.")

    except NetmikoAuthenticationException:
        print(f"❌ Error de autenticación en {ip}")
    except NetmikoTimeoutException:
        print(f"❌ Tiempo de espera agotado en {ip}")
    except Exception as e:
        print(f"❌ Ocurrió un error en {ip}: {e}")

if lineas_archivo_txt:
    with open(ruta_archivo_txt, "w", encoding="utf-8") as txtf:
        txtf.writelines(lineas_archivo_txt)

if lineas_archivo_csv:
    with open(ruta_archivo_csv, "w", newline="", encoding="utf-8") as csvf:
        csv_info = csv.writer(csvf, delimiter=";")
        csv_info.writerow(Header_csv)
        csv_info.writerows(lineas_archivo_csv)

    print(f"\n✅ Archivos guardados correctamente en: {os.path.abspath(carpeta_destino)}")
else:
    print("\n⚠️ No se recolectaron datos de ningún dispositivo para guardar.")

print("\n================ RECOLECCIÓN FINALIZADA ================")