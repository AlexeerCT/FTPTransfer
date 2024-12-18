import configparser
import ftplib
import paramiko
import os
import time
import logging
from datetime import datetime, timedelta

# Configurar logging
log_filename = f"transferencias_{datetime.now().strftime('%Y%m%d')}.log"
logging.basicConfig(
    filename=log_filename,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logging.info("Inicio del programa")

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
    logging.info(f"Conectándose al servidor FTP {ftp_config['host']}...")
    with ftplib.FTP(ftp_config["host"]) as ftp:
        ftp.login(ftp_config["user"], ftp_config["passwd"])
        logging.info("Conexión exitosa. Intentando descargar archivo...")
        try:
            with open(archivo_local, "wb") as archivo:
                ftp.retrbinary(f"RETR {archivo_remoto}", archivo.write)
            logging.info(f"Archivo descargado correctamente: {archivo_local}")
            ftp.delete(archivo_remoto)
            logging.info(f"Archivo remoto eliminado: {archivo_remoto}")
            return True
        except ftplib.error_perm as e:
            logging.warning(f"No se encontró el archivo remoto: {archivo_remoto}. Error: {e}")
            os.remove(archivo_local)
            return False

def subir_a_sftp(sftp_config, archivo_zip, remote_path):
    """Sube un archivo ZIP a un servidor SFTP."""
    logging.info(f"Conectándose al servidor SFTP {sftp_config['host']}...")
    transport = paramiko.Transport((sftp_config["host"], sftp_config["port"]))
    transport.connect(username=sftp_config["user"], password=sftp_config["passwd"])

    with paramiko.SFTPClient.from_transport(transport) as sftp:
        logging.info(f"Subiendo {archivo_zip} a {remote_path}...")
        sftp.put(archivo_zip, remote_path)
        logging.info("Archivo subido correctamente.")

    transport.close()

def main():
    """Función principal que gestiona la transferencia."""
    while True:
        try:
            # Calcular la fecha actual
            fecha_actual = datetime.now()
            logging.info(f"Fecha actual: {fecha_actual.strftime('%Y%m%d')}")

            # Intentar transferencias para MYS y FDM
            for prefijo, destino in [("MYSRECON", sftp_destino_mys), ("FDMRECON", sftp_destino_fdm)]:
                exito = False
                for dias in range(2):  # Intentar con el día actual y el anterior
                    fecha = (fecha_actual - timedelta(days=dias)).strftime("%Y%m%d")
                    archivo_local = f"{prefijo}_{fecha}.zip"
                    archivo_remoto = f"/Herramientas/IMMEX/GRUPO SION/{prefijo}_{fecha}.zip"

                    if descargar_desde_ftp(ftp_origen, archivo_local, archivo_remoto):
                        remote_path = f"{prefijo}_{fecha}.zip"
                        subir_a_sftp(destino, archivo_local, remote_path)
                        os.remove(archivo_local)
                        logging.info(f"Archivo local eliminado: {archivo_local}")
                        exito = True
                        break

                if not exito:
                    logging.warning(f"No se pudo transferir el archivo para {prefijo} en los últimos dos días.")

            logging.info("Transferencia completada. Esperando el próximo ciclo...")
        except Exception as e:
            logging.error(f"Error durante la transferencia: {e}")

        # Esperar antes de la siguiente comprobación
        time.sleep(intervalo)

if __name__ == "__main__":
    main()
