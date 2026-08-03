import subprocess
import json
import os
APPDATA = os.environ["APPDATA"]
MINECRAFT = os.path.join(APPDATA, ".minecraft")
VERSIONS = os.path.join(MINECRAFT, "versions")
LIBRARIES = os.path.join(MINECRAFT, "libraries")
classpath = os.path.join(VERSIONS, "1.20.1", "1.20.1.jar")+";"
with open(os.path.join(VERSIONS, "1.20.1", "1.20.1.json"), "r") as f:
    versionjson = json.load(f)
for lib in versionjson["libraries"]:
    if "downloads" in lib and "artifact" in lib["downloads"]:
        classpath += os.path.join(LIBRARIES, lib["downloads"]["artifact"]["path"])+";"
classpath = classpath[0:-1]
command = ["C://Program Files//Java//jdk-17//bin//java.exe", "-cp", classpath, "net.minecraft.client.main.Main", "--version", "1.20.1", "--versionType", "release", "--username", "Gyroslord5", "--uuid", "d6131ecd-caad-4049-a88e-76ad2cab490f", "--accessToken", "0"]
subprocess.run(command)