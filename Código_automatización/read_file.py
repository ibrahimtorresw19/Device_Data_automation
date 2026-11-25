import os
from netmiko import ConnectHandler
from netmiko.exceptions import NetmikoAuthenticationException, NetmikoTimeoutException

dispositivo = {
    "device_type": "cisco_ios",
    "host": "10.10.20.171",
    "username": "cisco",
    "password": "cisco",
    "secret": "cisco",
    "port": 22,
}

ruta_actual = os.getcwd()
print(ruta_actual)


def configuracion(carpeta="Configuraciones", documento="R1.txt"):
    comandos = []
    ruta_completa = os.path.join("..", carpeta, documento)
    ruta_r1_limpia = os.path.abspath(ruta_completa)
    print(ruta_r1_limpia)

    if not os.path.exists(ruta_r1_limpia):
        print("La ruta no es la correcta o dicha carpeta y archivo no existe")
        return False

    with open(ruta_r1_limpia, "r", encoding="utf-8") as archivo:
        for lineas in archivo:
            lineas_limpias = lineas.strip()
            if lineas_limpias and not lineas_limpias.startswith("!"):
                comandos.append(lineas_limpias)

    try:
        with ConnectHandler(**dispositivo) as connect:
            connect.enable()

            print(f"Archivo subido exitosamente. La cantidad de comandos son: {len(comandos)}")
            print("=============================RESPUESTA DEL DISPOSITIVO============================")
            envio_comandos = connect.send_config_set(comandos)
            print(envio_comandos)
            return True

    except NetmikoAuthenticationException:
        print("❌ Error de autenticación")
    except NetmikoTimeoutException:
        print("❌ Tiempo de espera agotado")
    except Exception as e:
        print(f"Ocurrió un error durante el proceso: {e}")

    return False


configuracion()