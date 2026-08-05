import os
import zipfile
import shutil
print("Starting Installation, wait until done")
def move_file(source, destination):
    with open(source, "rb") as f:
        bytes = f.read()
    with open(destination, "wb") as f:
        f.write(bytes)
TEMP = os.environ["TEMP"]
APPDATA = os.environ["APPDATA"]
PROGRAMS = os.path.join("C:\\", "ProgramData", "Microsoft", "Windows", "Start Menu", "Programs")
INSTALLATION = os.path.join("C:\\", "Program Files", "Gyros Client")
TEMP_INSTALLATION = os.path.join(TEMP, "gyrosclientinstallation")
APPDATA_INSTALLATION = os.path.join(APPDATA, "GyrosClient")
JAVA = os.path.join(APPDATA_INSTALLATION, "Java")
FILESZIP = os.path.abspath("files.zip")
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
with zipfile.ZipFile(os.path.join(TEMP_INSTALLATION, "resources.zip"), "r") as zip:
    zip.extractall(APPDATA_INSTALLATION)
with zipfile.ZipFile(os.path.join(TEMP_INSTALLATION, "profiles.zip"), "r") as zip:
    zip.extractall(APPDATA_INSTALLATION)
os.mkdir(JAVA)
with zipfile.ZipFile(os.path.join(TEMP_INSTALLATION, "java.zip", "r")) as zip:
    zip.extractall(JAVA)
shutil.rmtree(TEMP_INSTALLATION)
if os.path.exists(TEMP_INSTALLATION):
    os.rmdir()
print("Installation Done you can close this now.")
input("Press enter to exit...")