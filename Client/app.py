import requests
import subprocess
import json
import os
import customtkinter as ctk
import threading
APPDATA = os.environ["appdata"]
FILELOCATION = os.path.dirname(__file__)
RESOURCES = os.path.join(FILELOCATION, "resources")
VERSION_MANIFEST_URL = "https://piston-meta.mojang.com/mc/game/version_manifest_v2.json"
class Client:
    def __init__(self, username, version, modLoader, java, profilePath, versionPath, libraries, assetsPath):
        self.username = username
        self.version = version
        self.modLoader = modLoader
        self.java = java
        self.profilePath = profilePath
        self.versionPath = versionPath
        self.libraries = libraries
        self.assetsPath = assetsPath
        print("Initalizing Client...")
        with open(os.path.join(self.versionPath, self.version, f"{self.version}.json"), "r") as f:
            self.vanillajson = json.load(f)
        self.classpath = f"{os.path.join(self.versionPath, self.version, f"{self.version}.jar")};"
        for lib in self.vanillajson["libraries"]:
            if "downloads" in lib and "artifact" in lib["downloads"]:
                self.classpath += f"{os.path.join(self.libraries, lib["downloads"]["artifact"]["path"])};"
        if self.modLoader == "fabric":
            with open(os.path.join(self.versionPath, f"{self.modLoader}-{self.version}", f"{self.modLoader}-{self.version}.json"), "r") as f:
                self.fabricjson = json.load(f)
            for lib in self.fabricjson["libraries"]:
                group, artifact, artifactVersion = lib["name"].split(sep=":")
                self.classpath += f"{os.path.join(self.libraries, group.replace(".", os.sep), artifact, artifactVersion, f"{artifact}-{artifactVersion}.jar")};"
        self.classpath = self.classpath[0:-1]
        if self.modLoader == "fabric":startCommand = [self.java[self.vanillajson["javaVersion"]["majorVersion"]], "-cp", self.classpath, self.fabricjson["mainClass"], "--username", self.username, "--version", self.version, "--versionType", "release", "--accessToken", "0", "--gameDir", self.profilePath, "--assetsDir", self.assetsPath, "--assetIndex", self.vanillajson["assetIndex"]["id"]] 
        else: startCommand = [self.java[self.vanillajson["javaVersion"]["majorVersion"]], "-cp", self.classpath, self.vanillajson["mainClass"], "--username", self.username, "--version", self.version, "--versionType", "release", "--accessToken", "0", "--gameDir", self.profilePath, "--assetsDir", self.assetsPath, "--assetIndex", self.vanillajson["assetIndex"]["id"]]
        self.start(startCommand)

    def start(self, command):
        subprocess.run(command)
        del self



class App(ctk.CTk):
    def __init__(self, screenX, screenY):
        super().__init__()
        self.title("Gyros Client")
        self.geometry(f"{screenX}x{screenY}")
        self.version = "26.1.2"
        self.modLoaders = ["fabric", "vanilla"]
        self.modLoader = self.modLoaders[0]
        self.download_thread = None
        self.uiElements = []
        self.versionManifest = self.url_to_dic(VERSION_MANIFEST_URL)
        self.java = {
            17 : "C://Program Files//Java//jdk-17//bin//java.exe",
            21 : "C://Program Files//Java//jdk-21//bin//java.exe",
            25 : "C://Program Files//Java//jdk-25//bin//java.exe"
        }
        self.drawUI()
    def url_to_dic(self, url):
        request = requests.get(url)
        return request.json()
    def downloadThread(self, url, absolutePathWithFileName):
        request = requests.get(url)
        with open(absolutePathWithFileName, "wb") as f:
            f.write(request.content)
    def wait_until_download_thread_done(self, callback):
        if self.download_thread.is_alive():
            self.after(50, lambda: self.wait_until_download_thread_done(callback))
        else:
            callback()
    def url_to_file(self, url, absolutePathWithFileName):
        self.download_thread = threading.Thread(target=lambda: self.downloadThread(url, absolutePathWithFileName))
        if not self.download_thread.is_alive():
            self.download_thread.start()
    def dic_to_json(self, dic, absolutePathWithFileName):
        with open(absolutePathWithFileName, "w") as f:
            json.dump(dic, f, indent=4)
    def drawUI(self):
        for element in self.uiElements:
            element.destroy()
        self.uiElements.clear()
        self.nameText = ctk.CTkLabel(self, text="Gyros Client", font=("Bold", 40))
        self.nameText.place(x=475, y=50)
        self.playButtton = ctk.CTkButton(self, width=250, height=125, text=f"Play {self.version} - {self.modLoader[0].upper()}{self.modLoader[1:]}", font=("Bold", 40), command=self.startClient)
        self.playButtton.place(x=410, y=450)
        self.modLoaderDropdown = ctk.CTkComboBox(self, values=self.modLoaders, command=self.versionTypeDropdown_callback, state="readonly", width=250, height=60, font=("Bold", 40))
        self.modLoaderDropdown.set(self.modLoader)
        self.modLoaderDropdown.place(x=470, y=330)
        self.uiElements.append(self.nameText)
        self.uiElements.append(self.playButtton)
        self.uiElements.append(self.modLoaderDropdown)
        
    def startClient(self):
        thread = threading.Thread(target=lambda: self.runClient("Gyroslord5", self.version, self.modLoader, self.java, os.path.join(FILELOCATION, "profiles", "default"), os.path.join(RESOURCES, "versions"), os.path.join(RESOURCES, "libraries"), os.path.join(RESOURCES, "assets")))
        if self.modLoader == "vanilla":
            if not os.path.exists(os.path.join(RESOURCES, "versions", self.version)):
                for version in self.versionManifest["versions"]:
                    if version["id"] == self.version:
                        version_dic = self.url_to_dic(version["url"])
                downloadPath = os.path.join(RESOURCES, "versions", self.version)
                os.mkdir(downloadPath)
                self.url_to_file(version_dic["downloads"]["client"]["url"], os.path.join(downloadPath, f"{self.version}.jar"))
                self.dic_to_json(version_dic, os.path.join(RESOURCES, "versions", self.version, f"{self.version}.json"))
                self.wait_until_download_thread_done(thread.start)
            else:
                thread.start()
    def runClient(self, username, version, modLoader, java, profilePath, versionPath, libraries, assetsPath):
        Client(username, version, modLoader, java, profilePath, versionPath, libraries, assetsPath)
    def versionTypeDropdown_callback(self, selection):
        self.modLoader = selection
        self.playButtton.configure(text=f"Play {self.version} - {self.modLoader[0].upper()}{self.modLoader[1:]}")
app = App(1200, 700)
app.mainloop()