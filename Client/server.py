import os
import requests
import subprocess
VERSION_MANIFEST_URL = "https://piston-meta.mojang.com/mc/game/version_manifest_v2.json"
VERSION_MANIFEST = None
class Server:
    def __init__(self, server, version, modloader, ram, java):
        self.server, self.version, self.modloader, self.ram, self.java = server, version, modloader, ram, java

    def download_file(self, url, output):
        request = requests.get(url)
        with open(output, "wb") as f:
            f.write(request.content)

    def url_to_dic(self, url):
        request = requests.get(url)
        return request.json()
    
    def start(self):
        if self.modloader == "vanilla":
            VERSION_MANIFEST = self.url_to_dic(VERSION_MANIFEST_URL)
            for versionObj in VERSION_MANIFEST["versions"]:
                if versionObj["type"] == "release":
                    if versionObj["id"] == self.version:
                        version_dic = self.url_to_dic(versionObj["url"])
                        break
            if not os.path.exists(os.path.join(self.server, "server.jar")):
                self.download_file(version_dic["downloads"]["server"]["url"], os.path.join(self.server, "server.jar"))
            return [self.java, f"-Xmx{self.ram}G", f"-Xms{self.ram}G", "-jar", "server.jar", "nogui"], self.server