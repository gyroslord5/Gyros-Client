import requests
import subprocess
import json
import os
import customtkinter as ctk
import threading
APPDATA = os.environ["appdata"]
FILELOCATION = os.path.dirname(__file__)
RESOURCES = os.path.join(FILELOCATION, "resources")
class Client:
    def __init__(self, username, version, versionType, java, profilePath, versionPath, libraries, assetsPath):
        self.username = username
        self.version = version
        self.versionType = versionType
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
        if self.versionType == "fabric":
            with open(os.path.join(self.versionPath, f"{self.versionType}-{self.version}", f"{self.versionType}-{self.version}.json"), "r") as f:
                self.fabricjson = json.load(f)
            for lib in self.fabricjson["libraries"]:
                group, artifact, artifactVersion = lib["name"].split(sep=":")
                self.classpath += f"{os.path.join(self.libraries, group.replace(".", os.sep), artifact, artifactVersion, f"{artifact}-{artifactVersion}.jar")};"
        self.classpath = self.classpath[0:-1]
        if self.versionType == "fabric":startCommand = [self.java[self.vanillajson["javaVersion"]["majorVersion"]], "-cp", self.classpath, self.fabricjson["mainClass"], "--username", self.username, "--version", self.version, "--versionType", "release", "--accessToken", "0", "--gameDir", self.profilePath, "--assetsDir", self.assetsPath, "--assetIndex", self.vanillajson["assetIndex"]["id"]] 
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
        self.versionTypes = ["fabric", "vanilla"]
        self.versionType = self.versionTypes[0]
        self.uiElements = []
        self.java = {
            17 : "C://Program Files//Java//jdk-17//bin//java.exe",
            21 : "C://Program Files//Java//jdk-21//bin//java.exe",
            25 : "C://Program Files//Java//jdk-25//bin//java.exe"
        }
        self.drawUI()
    def drawUI(self):
        for element in self.uiElements:
            element.destroy()
        self.uiElements.clear()
        self.nameText = ctk.CTkLabel(self, text="Gyros Client", font=("Bold", 40))
        self.nameText.place(x=475, y=50)
        self.playButtton = ctk.CTkButton(self, width=250, height=125, text=f"Play {self.version} - {self.versionType[0].upper()}{self.versionType[1:]}", font=("Bold", 40), command=self.startClient)
        self.playButtton.place(x=410, y=450)
        self.versionTypeDropdown = ctk.CTkComboBox(self, values=self.versionTypes, command=self.versionTypeDropdown_callback, state="readonly", width=250, height=60, font=("Bold", 40))
        self.versionTypeDropdown.set(self.versionType)
        self.versionTypeDropdown.place(x=470, y=330)
        self.uiElements.append(self.nameText)
        self.uiElements.append(self.playButtton)
        self.uiElements.append(self.versionTypeDropdown)
        
    def startClient(self):
        thread = threading.Thread(target=lambda: self.runClient("Gyroslord5", self.version, self.versionType, self.java, os.path.join(FILELOCATION, "profiles", "default"), os.path.join(RESOURCES, "versions"), os.path.join(RESOURCES, "libraries"), os.path.join(RESOURCES, "assets")))
        thread.start()
    def runClient(self, username, version, versionType, java, profilePath, versionPath, libraries, assetsPath):
        Client(username, version, versionType, java, profilePath, versionPath, libraries, assetsPath)
    def versionTypeDropdown_callback(self, selection):
        self.versionType = selection
        self.playButtton.configure(text=f"Play {self.version} - {self.versionType[0].upper()}{self.versionType[1:]}")
app = App(1200, 700)
app.mainloop()