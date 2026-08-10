import os
import zipfile
import shutil
import requests
import ctypes
def move_file(source, destination):
    with open(source, "rb") as f:
        bytes = f.read()
    with open(destination, "wb") as f:
        f.write(bytes)
def downloadFile(url, path):
    request = requests.get(url)
    with open(path, "wb") as f:
        f.write(request.content)
TEMP = os.environ["TEMP"]
APPDATA = os.environ["APPDATA"]
PROGRAMS = os.path.join("C:\\", "ProgramData", "Microsoft", "Windows", "Start Menu", "Programs")
INSTALLATION = os.path.join("C:\\", "Program Files", "Gyros Client")
TEMP_INSTALLATION = os.path.join(TEMP, "gyrosclientinstallation")
APPDATA_INSTALLATION = os.path.join(APPDATA, "GyrosClient")
JAVA = os.path.join(APPDATA_INSTALLATION, "Java")
FILESZIP = os.path.abspath("files.zip")
JAVAURLS = {
    17 : "https://download.oracle.com/java/17/archive/jdk-17.0.12_windows-x64_bin.zip",
    21 : "https://download.oracle.com/java/21/latest/jdk-21_windows-x64_bin.zip",
    25 : "https://download.oracle.com/java/25/latest/jdk-25_windows-x64_bin.zip"
}
if ctypes.windll.shell32.IsUserAnAdmin():
    print("Starting Installation, wait until done")
    print("[LOG] Extracting all neccesary files into: "+TEMP_INSTALLATION)
    if not os.path.exists(TEMP_INSTALLATION):
        os.mkdir(TEMP_INSTALLATION)
    if not os.path.exists(INSTALLATION):
        os.mkdir(INSTALLATION)
    if not os.path.exists(APPDATA_INSTALLATION):
        os.mkdir(APPDATA_INSTALLATION)
    with zipfile.ZipFile(FILESZIP, "r") as zip:
        zip.extractall(TEMP_INSTALLATION)
    move_file(os.path.join(TEMP_INSTALLATION, "shortcut.lnk"), os.path.join(PROGRAMS, "Gyros Client.lnk"))
    with zipfile.ZipFile(os.path.join(TEMP_INSTALLATION, "app.zip"), "r") as zip:
        zip.extractall(INSTALLATION)
    with zipfile.ZipFile(os.path.join(TEMP_INSTALLATION, "profiles.zip"), "r") as zip:
        zip.extractall(APPDATA_INSTALLATION)
    os.makedirs(JAVA, exist_ok=True)
    os.makedirs(os.path.join(APPDATA_INSTALLATION, "Servers"), exist_ok=True)
    print("[LOG] Downloading JDK-17...")
    downloadFile(JAVAURLS[17], os.path.join(TEMP_INSTALLATION, "jdk-17.zip"))
    print("[LOG] Downloading JDK-21...")
    downloadFile(JAVAURLS[21], os.path.join(TEMP_INSTALLATION, "jdk-21.zip"))
    print("[LOG] Downloading JDK-25...")
    downloadFile(JAVAURLS[25], os.path.join(TEMP_INSTALLATION, "jdk-25.zip"))
    print("[LOG] Extracting JDK-17...")
    with zipfile.ZipFile(os.path.join(TEMP_INSTALLATION, "jdk-17.zip")) as zip:
        zip.extractall(JAVA)
    os.rename(os.path.join(JAVA, "jdk-17.0.12"), os.path.join(JAVA, "jdk-17"))
    print("[LOG] Extracting JDK-21...")
    with zipfile.ZipFile(os.path.join(TEMP_INSTALLATION, "jdk-21.zip")) as zip:
        zip.extractall(JAVA)
    os.rename(os.path.join(JAVA, "jdk-21.0.12"), os.path.join(JAVA, "jdk-21"))
    print("[LOG] Extracting JDK-25...")
    with zipfile.ZipFile(os.path.join(TEMP_INSTALLATION, "jdk-25.zip")) as zip:
        zip.extractall(JAVA)
    os.rename(os.path.join(JAVA, "jdk-25.0.4"), os.path.join(JAVA, "jdk-25"))
    print("[LOG] Cleaning up temporary files...")
    shutil.rmtree(TEMP_INSTALLATION)
    if os.path.exists(TEMP_INSTALLATION):
        os.rmdir()
    print("Installation Done you can close this now.")
else:
    print("You need to start the Application with Admin rights to Install Gyros Client")
input("Press enter to exit...")