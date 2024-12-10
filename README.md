# FTP-SFTP File Transfer

This project automates the process of transferring files from an FTP server to two separate SFTP servers. It periodically downloads files from the FTP server, uploads them to the SFTP servers, and cleans up local copies after successful transfers.

## Features
- Download files from an FTP server.
- Upload files to multiple SFTP servers.
- Periodic execution with customizable intervals.
- Configuration-driven setup using a `config.ini` file.

---

## Prerequisites

- **Python 3.6+**
- The following Python libraries:
  - `configparser`
  - `ftplib`
  - `paramiko`
  - `os`
  - `time`
  - `datetime`

You can install any missing dependencies with pip:

```bash
pip install paramiko
```

---

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/AlexeerCT/FTPTransfer
cd FTPTransfer
```

### 2. Create a `config.ini` file

Create a configuration file in the root directory named `config.ini` with the following structure:

```ini
[FTP_ORIGEN]
host = ftp.example.com
user = your_ftp_username
passwd = your_ftp_password

[SFTP_DESTINO_MYS]
host = sftp1.example.com
user = your_sftp1_username
passwd = your_sftp1_password
port = 22

[SFTP_DESTINO_FDM]
host = sftp2.example.com
user = your_sftp2_username
passwd = your_sftp2_password
port = 22
```

### 3. Configure File Paths

The file paths for downloading and uploading are defined in the script. Ensure they match your requirements. Modify the `archivo_remoto_mys` and `archivo_remoto_fdm` variables if necessary.

### 4. Run the Script

Execute the script to start the file transfer process:

```bash
python FTP.py
```

---

## How It Works

1. **Download Files**
   - The script connects to the FTP server and downloads files based on the current date.
   
2. **Upload Files**
   - The downloaded files are then uploaded to two SFTP servers, each with its own configuration.

3. **Cleanup**
   - After successful uploads, the script removes the local copies of the files.
   - Después de cargas exitosas, el script elimina el archivo ftp de su ruta original. 

4. **Repetition**
   - The process repeats at the interval defined in the `intervalo` variable (default: 7200 seconds). 7200 seconds = 2 hours

---

## Error Handling
- If an error occurs during any stage of the process, it will be logged to the console.
- The script will wait for the next interval and retry.

---

## Customization
- **Interval**: Change the `intervalo` variable to adjust the frequency of execution.
- **File Names**: Modify the naming conventions in the script if necessary.

---

## License
This project is licensed under the MIT License. See the `LICENSE` file for details.

---

## Contributing
Feel free to fork this repository and submit pull requests with enhancements or bug fixes.

