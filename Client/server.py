import os
import sys
import requests
import subprocess
args = sys.argv
VERSION_MANIFEST_URL = "https://piston-meta.mojang.com/mc/game/version_manifest_v2.json"
VERSION_MANIFEST = None
def download_file(url, output):
    request = requests.get(url)
    with open(output, "wb") as f:
        f.write(request.content)
def url_to_dic(url):
    request = requests.get(url)
    return request.json()
def start():
    try:
        app, server, version, modloader, ram, java = args
    except ValueError:
        print("You have to start this program with 5 arguments: server, version, modloader, ram, java")
        exit()
    if modloader == "vanilla":
        VERSION_MANIFEST = url_to_dic(VERSION_MANIFEST_URL)
        for versionObj in VERSION_MANIFEST["versions"]:
                    if versionObj["type"] == "release":
                        if versionObj["id"] == version:
                            version_dic = url_to_dic(versionObj["url"])
                            break
        if not os.path.exists(os.path.join(server, "server.jar")):
            download_file(version_dic["downloads"]["server"]["url"], os.path.join(server, "server.jar"))
        subprocess.run([java, f"-Xmx{ram}G", f"-Xms{ram}G", "-jar", "server.jar", "nogui"], cwd=server)
start()