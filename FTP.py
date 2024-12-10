import configparser
import ftplib
import paramiko
import os
import time
from datetime import datetime

# Leer archivo .ini
config = configparser.ConfigParser(interpolation=None)
config.read("config.ini")

# Configuración del servidor FTP (origen)
ftp_origen = {
    "host": config["FTP_ORIGEN"]["host"],
    "user": config["FTP_ORIGEN"]["user"],
    "passwd": config["FTP_ORIGEN"]["passwd"],
}

# Configuración de los servidores SFTP (destino)
sftp_destino_mys = {
    "host": config["SFTP_DESTINO_MYS"]["host"],
    "user": config["SFTP_DESTINO_MYS"]["user"],
    "passwd": config["SFTP_DESTINO_MYS"]["passwd"],
    "port": int(config["SFTP_DESTINO_MYS"]["port"]),
}

sftp_destino_fdm = {
    "host": config["SFTP_DESTINO_FDM"]["host"],
    "user": config["SFTP_DESTINO_FDM"]["user"],
    "passwd": config["SFTP_DESTINO_FDM"]["passwd"],
    "port": int(config["SFTP_DESTINO_FDM"]["port"]),
}

# Tiempo entre comprobaciones (en segundos)
intervalo = 7200

def descargar_desde_ftp(ftp_config, archivo_local, archivo_remoto):
    """Descarga un archivo desde un servidor FTP."""
    print(f"Conectándose al servidor FTP {ftp_config['host']}...")
    with ftplib.FTP(ftp_config["host"]) as ftp:
        ftp.login(ftp_config["user"], ftp_config["passwd"])
        print("Conexión exitosa. Descargando archivo...")
        with open(archivo_local, "wb") as archivo:
            ftp.retrbinary(f"RETR {archivo_remoto}", archivo.write)
        print(f"Archivo descargado correctamente: {archivo_local}")


def subir_a_sftp(sftp_config, archivo_zip, remote_path):
    """Sube un archivo ZIP a un servidor SFTP."""
    print(f"Conectándose al servidor SFTP {sftp_config['host']}...")
    transport = paramiko.Transport((sftp_config["host"], sftp_config["port"]))
    transport.connect(username=sftp_config["user"], password=sftp_config["passwd"])

    with paramiko.SFTPClient.from_transport(transport) as sftp:
        print(f"Subiendo {archivo_zip} a {remote_path}...")
        sftp.put(archivo_zip, remote_path)
        print("Archivo subido correctamente.")

    transport.close()


def main():
    """Función principal que gestiona la transferencia."""
    while True:
        try:
            # Calcular la fecha actual
            fecha_actual = datetime.now().strftime("%Y%m%d")
            print(f"Fecha actual: {fecha_actual}")

            # Rutas y nombres de los archivos
            archivo_local_mys = f"MYSRECON_{fecha_actual}.zip"
            archivo_local_fdm = f"FDMRECON_{fecha_actual}.zip"

            archivo_remoto_mys = f"/Herramientas/IMMEX/GRUPO SION/MYSRECON_{fecha_actual}.zip"
            archivo_remoto_fdm = f"/Herramientas/IMMEX/GRUPO SION/FDMRECON_{fecha_actual}.zip"

            remote_path_mys = f"MYSRECON_{fecha_actual}.zip"
            remote_path_fdm = f"FDMRECON_{fecha_actual}.zip"

            print("Iniciando proceso de transferencia...")

            # Descargar los dos archivos desde FTP
            descargar_desde_ftp(ftp_origen, archivo_local_mys, archivo_remoto_mys)
            descargar_desde_ftp(ftp_origen, archivo_local_fdm, archivo_remoto_fdm)

            # Subir el primer archivo al primer servidor SFTP
            subir_a_sftp(sftp_destino_mys, archivo_local_mys, remote_path_mys)

            # Subir el segundo archivo al segundo servidor SFTP
            subir_a_sftp(sftp_destino_fdm, archivo_local_fdm, remote_path_fdm)

            # Eliminar archivos locales después de la transferencia
            os.remove(archivo_local_mys)
            os.remove(archivo_local_fdm)
            print("Archivos locales eliminados.")

            print("Transferencia completada. Esperando el próximo ciclo...")
        except Exception as e:
            print(f"Error durante la transferencia: {e}")

        # Esperar antes de la siguiente comprobación
        time.sleep(intervalo)


if __name__ == "__main__":
    main()
