import requests
import subprocess
import json
import os
import customtkinter as ctk
import threading
from concurrent.futures import ThreadPoolExecutor
import server
APPDATA = os.environ["appdata"]
GYROSCLIENT = os.path.join(APPDATA, "GyrosClient")
RESOURCES = os.path.join(GYROSCLIENT, "resources")
PROFILES = os.path.join(GYROSCLIENT, "profiles")
APP_INSTALL = os.path.join("c:\\", "Program Files", "Gyros Client", "app")
SERVERS = os.path.join(GYROSCLIENT, "Servers")
BASE_FABRIC_URL = "https://maven.fabricmc.net/"
MINECRAFT_BASE_ASSET_URL = "https://resources.download.minecraft.net/"
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

    def initClient(self):
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
        self.classpath += self.maven_to_file_path(os.path.join(RESOURCES, "libraries"), self.fabricjson["loader"]["maven"])
        for lib in self.fabricjson["launcherMeta"]["libraries"]["common"]:
            self.classpath += self.maven_to_file_path(os.path.join(RESOURCES, "libraries"), lib["name"])
        self.classpath = self.classpath[0:-1]
        if self.modLoader == "fabric":startCommand = [self.java[self.vanillajson["javaVersion"]["majorVersion"]], "-cp", self.classpath, self.fabricjson["launcherMeta"]["mainClass"]["client"], "--username", self.username, "--version", self.version, "--versionType", "release", "--accessToken", "0", "--gameDir", self.profilePath, "--assetsDir", self.assetsPath, "--assetIndex", self.vanillajson["assetIndex"]["id"]] 
        else: startCommand = [self.java[self.vanillajson["javaVersion"]["majorVersion"]], "-cp", self.classpath, self.vanillajson["mainClass"], "--username", self.username, "--version", self.version, "--versionType", "release", "--accessToken", "0", "--gameDir", self.profilePath, "--assetsDir", self.assetsPath, "--assetIndex", self.vanillajson["assetIndex"]["id"]]
        proccess = self.start(startCommand)
        return proccess

    def maven_to_file_path(self, basePath, maven):
        group, artifact, artifactVersion = maven.split(sep=":")
        return f"{os.path.join(basePath, group.replace(".", "\\"), artifact, artifactVersion, f"{artifact}-{artifactVersion}.jar")};"

    def start(self, command):
        return subprocess.Popen(command)
        del self



class App(ctk.CTk):

    def __init__(self, screenX, screenY):
        super().__init__()
        self.title("Gyros Client")
        self.geometry(f"{screenX}x{screenY}")
        self.screenX = screenX
        self.screenY = screenY
        self.version = "26.1.2"
        self.modLoaders = ["fabric", "vanilla"]
        self.modLoader = self.modLoaders[0]
        self.versionManifest = self.url_to_dic(VERSION_MANIFEST_URL)
        self.versions = []
        self.clientProccess = None
        self.currentMenuFrame = self.currentMenuFrame = ctk.CTkFrame(self, width=1020, height=640, fg_color="gray14")
        self.currentMenuFrame.place(x=175, y=10)
        self.pool = ThreadPoolExecutor(16)
        self.selectedServer = "None"
        self.serverRunning = False
        self.futures = []
        self.profile = os.path.join(PROFILES, "default")
        self.profiles = []
        self.profileFrames = []
        self.serverProccess = None
        threading.Thread(target=self.handleInput).start()
        for version in self.versionManifest["versions"]:
                    if version["type"] == "release":
                        self.versions.append(version["id"])
        self.java = {
            17 : os.path.join(GYROSCLIENT, "Java", "jdk-17", "bin", "java.exe"),
            21 : os.path.join(GYROSCLIENT, "Java", "jdk-21", "bin", "java.exe"),
            25 : os.path.join(GYROSCLIENT, "Java", "jdk-25", "bin", "java.exe")
        }
        if not os.path.exists(RESOURCES):
            os.mkdir(RESOURCES)
            os.mkdir(os.path.join(RESOURCES, "assets"))
            os.mkdir(os.path.join(RESOURCES, "versions"))
            os.mkdir(os.path.join(RESOURCES, "libraries"))
        self.drawUniversalUI()
        self.drawMainScreen()
        
    def handleInput(self):
        inp = input()
        if self.serverProccess is not None:
            if self.serverProccess.poll() is None:
                self.serverProccess.stdin.write(f"{inp}\n")
                self.serverProccess.stdin.flush()
        self.handleInput()

    def url_to_dic(self, url):
        request = requests.get(url)
        return request.json()

    def updateStatusText(self, str):
        self.statusText.configure(text=str)

    def downloadThread(self, url, absolutePathWithFileName):
        request = requests.get(url)
        filename = os.path.basename(absolutePathWithFileName)
        app.after(0, lambda: self.updateStatusText(f"Installing: {filename}"))
        os.makedirs(os.path.dirname(absolutePathWithFileName), exist_ok=True)

        with open(absolutePathWithFileName, "wb") as f:
            f.write(request.content)

    def url_to_file(self, url, absolutePathWithFileName):
        self.futures.append(self.pool.submit(self.downloadThread, url, absolutePathWithFileName))

    def dic_to_json(self, dic, absolutePathWithFileName):
        with open(absolutePathWithFileName, "w") as f:
            json.dump(dic, f, indent=4)

    def versionsDropdown_callback(self, selection):
        self.versionDropdown.set(selection)
        if selection in self.versions: self.version = selection

    def drawUniversalUI(self):
        self.nameText = ctk.CTkLabel(self, text="Gyros Client", font=("Bold", 40))
        self.nameText.place(relx=0.525, y=50, anchor="center")
        self.sideBar = ctk.CTkScrollableFrame(self, width=150, height=681)
        self.sideBar.place(x=0, y=10)
        self.statusText = ctk.CTkLabel(self, text="", font=("Bold", 22), anchor="center", justify="center")
        self.statusText.place(relx=0.525, rely=0.65, anchor="center")
        self.menuBar = ctk.CTkFrame(self, width=400, height=50, fg_color="gray10")
        self.menuBar.place(relx=0.525, y=675, anchor="center")
        self.mainMenuButton = ctk.CTkButton(self.menuBar, width=30, height=30, text="Main", command=self.drawMainScreen)
        self.mainMenuButton.place(x=35, rely=0.5, anchor="center")
        self.serverMenuButton = ctk.CTkButton(self.menuBar, width=30, height=30, text="Servers", command=self.drawServersMenu)
        self.serverMenuButton.place(x=100, rely=0.5, anchor="center")

    def drawMainScreen(self):
        for object in self.currentMenuFrame.winfo_children():
            object.destroy()
        for object in self.sideBar.winfo_children():
            object.destroy()
        self.playButtton = ctk.CTkButton(self.currentMenuFrame, width=250, height=125, text=f"Play: {os.path.basename(self.profile)}", font=("Bold", 40), command=self.playButton_callback)
        self.playButtton.place(relx=0.45, y=530, anchor="center")
        self.activeProfile = ctk.CTkLabel(self.currentMenuFrame, text=f"Selected Profile: {os.path.basename(self.profile)}", font=("Bold", 22))
        self.activeProfile.place(relx=0.45, y=90, anchor="center")
        self.toolbarFrame = ctk.CTkFrame(self, width=155, height=45, fg_color="gray15", corner_radius=15, bg_color="gray15")
        self.toolbarFrame.place(x=0, y=665)
        self.refreshButton = ctk.CTkButton(self.toolbarFrame, text="Refresh", bg_color="gray15", width=30, command=self.updateProfiles)
        self.refreshButton.place(x=120, rely=0.4, anchor="center")
        self.createProfileButton = ctk.CTkButton(self.toolbarFrame, text="+", width=30, command=self.drawCreateProfileMenu)
        self.createProfileButton.place(x=5, y=5)
        self.updateProfiles()

    def updateServers(self):
        temp = []
        for element in os.listdir(SERVERS):
            if os.path.isdir(os.path.join(SERVERS, element)):
                temp.append(element)
        self.servers = temp
        for frame in self.sideBar.winfo_children():
            frame.destroy()
        for server in self.servers:
            frame = ctk.CTkFrame(self.sideBar, width=140, height=90, fg_color="gray10")
            frame.pack(pady=5)
            profileNameText = ctk.CTkLabel(frame, text=server, font=("Bold", 14))
            profileNameText.place(x=70, y=30, anchor="center")
            self.selectServerButtons = []
            button = ctk.CTkButton(frame, text="Select Server", width=120, command=lambda server=server: self.setServer(server))
            self.selectServerButton.append(button)
            button.place(x=10, y=55)


    def drawServersMenu(self):
        for object in self.currentMenuFrame.winfo_children():
            object.destroy()
        for frame in self.sideBar.winfo_children():
            frame.destroy()
        for object in self.toolbarFrame.winfo_children():
            object.destroy()
        self.updateServers()
        if not self.serverRunning:
            self.startServerButtton = ctk.CTkButton(self.currentMenuFrame, width=250, height=125, text=f"Start: {os.path.basename(self.selectedServer)}", font=("Bold", 40), command=self.startServerButtonClicked)
            self.startServerButtton.place(relx=0.45, y=530, anchor="center")
        else:
            self.startServerButtton = ctk.CTkButton(self.currentMenuFrame, width=250, height=125, text=f"Stop: {os.path.basename(self.selectedServer)}", font=("Bold", 40), command=self.stopServer, fg_color="red", hover_color="#7B2320")
            self.startServerButtton.place(relx=0.45, y=530, anchor="center")
        self.createServerButton = ctk.CTkButton(self.toolbarFrame, text="+", width=30, command=self.drawCreateServerMenu)
        self.createServerButton.place(x=5, y=5)


    def startServerButtonClicked(self):
        if self.selectedServer == "None":
            self.after(0, lambda: self.updateStatusText("You need to select an server!"))
        else:
            threading.Thread(target=lambda: self.startServer(os.path.join(SERVERS, self.selectedServer), self.serverJson["version"], self.serverJson["modloader"], self.serverJson["ram"], self.java[self.serverJson["java"]])).start()

    def startServer(self, serverPath, version, modloader, ram, java):
        self.serverRunning = True
        self.after(0, lambda: self.updateStatusText("Starting Server..."))
        self.after(10000, lambda: self.updateStatusText(""))
        serverManager = server.Server(serverPath, version, modloader, ram, java)
        argv, wd = serverManager.start()
        self.serverProccess = subprocess.Popen(argv, cwd=wd, stdin=subprocess.PIPE, text=True)
        threading.Thread(target=self.waitForServer).start()
        for button in self.selectServerButtons:
            button.configure(state="disabled")
        self.startServerButtton.configure(text=f"Stop: {os.path.basename(self.selectedServer)}", fg_color="red", hover_color="#7B2320", command=self.stopServer, width=250, height=125, state="disabled")
        self.after(10000, lambda: self.startServerButtton.configure(state="normal"))

    def waitForServer(self):
        self.serverProccess.wait()
        self.startServerButtton.configure(text=f"Start: {os.path.basename(self.selectedServer)}", fg_color="#1F538D", hover_color="#1C487A", command=self.startServerButtonClicked)
        

    def stopServer(self):
        self.serverRunning = False
        self.after(0, lambda: self.updateStatusText("Stopping Server..."))
        self.after(2000, lambda: self.updateStatusText(""))
        self.serverProccess.stdin.write("stop\n")
        self.serverProccess.stdin.flush()

    def file_to_dic(self, file):
        with open(file, "r") as f:
            dic = json.load(f)
        return dic

    def setServer(self, server):
        self.selectedServer = server
        self.serverJson = self.file_to_dic(os.path.join(SERVERS, self.selectedServer, "gyrosclient.json"))
        if self.startServerButtton is not None:
            self.startServerButtton.configure(text=f"Start: {os.path.basename(self.selectedServer)}")

    def setProfile(self, profile):
        self.profile = profile
        self.activeProfile.configure(text=f"Selected Profile: {os.path.basename(self.profile)}")
        self.playButtton.update()
        self.playButtton.configure(text=f"Play: {os.path.basename(self.profile)}")

    def drawCreateProfileMenu(self):
        self.playButtton.configure(state="disabled")
        self.createProfileButton.configure(state="disabled")
        self.createProfileMenu = ctk.CTkFrame(self, width=400, height=300)
        self.createProfileMenu.place(relx=0.525, rely=0.4, anchor="center")
        self.nameInputField = ctk.CTkEntry(self.createProfileMenu, placeholder_text="Enter Profile Name: ", width=300, height=40)
        self.nameInputField.place(relx=0.5, y=50, anchor="center")
        self.deditatedwamInput = ctk.CTkEntry(self.createProfileMenu, width=250, height=40, placeholder_text="RAM (in GB): Default=2")
        self.deditatedwamInput.place(relx=0.5, y=100, anchor="center")
        self.versionDropdown = ctk.CTkComboBox(self.createProfileMenu, values=self.versions, width=250, height=45, font=("Bold", 26), command=self.versionsDropdown_callback)
        self.versionDropdown.set("26.1.2")
        self.versionDropdown.place(relx=0.5, y=150, anchor="center")
        self.modLoaderDropdown = ctk.CTkComboBox(self.createProfileMenu, values=self.modLoaders, command=self.modLoaderDropdown_callback, state="readonly", width=250, height=45, font=("Bold", 26))
        self.modLoaderDropdown.set(self.modLoader)
        self.modLoaderDropdown.place(relx=0.5, y=200, anchor="center")
        self.createButton = ctk.CTkButton(self.createProfileMenu, text="Create", command= lambda:self.createProfile(self.nameInputField.get(), self.modLoaderDropdown.get(), self.versionDropdown.get(), self.deditatedwamInput.get()))
        self.createButton.place(x=200, y=265, anchor="center")
        self.closeButton = ctk.CTkButton(self.createProfileMenu, fg_color="red", hover_color="#7B2320", text="X", command=self.closeProfileMenu, width=30, height=30)
        self.closeButton.place(relx=0.95, rely=0.075, anchor="center")

    def closeProfileMenu(self):
        self.createProfileMenu.destroy()
        self.playButtton.configure(state="normal")
        self.createProfileButton.configure(state="normal")

    def drawCreateServerMenu(self):
        self.createServerMenu = ctk.CTkFrame(self.currentMenuFrame, fg_color="gray10", width=500, height=350)
        self.createServerMenu.place(x=215, y=70)
        self.createServerStatusText = ctk.CTkLabel(self.createServerMenu, text="")
        self.createServerStatusText.place(relx=0.5, rely=0.88, anchor="center")
        self.createServerText = ctk.CTkLabel(self.createServerMenu, text="Create Server", font=("Bold", 22))
        self.createServerText.place(relx=0.5, rely=0.075, anchor="center")
        self.nameInput = ctk.CTkEntry(self.createServerMenu, width=300, placeholder_text="Enter Server name: ", height=56)
        self.nameInput.place(relx=0.5, rely=0.2, anchor="center")
        self.wamInput = ctk.CTkEntry(self.createServerMenu, width=300, placeholder_text="Ram (Default=4GB): ", height=56)
        self.wamInput.place(relx=0.5, rely=0.4, anchor="center")
        self.serverVersionDropdown = ctk.CTkComboBox(self.createServerMenu, width=250, height=45, values=self.versions)
        self.serverVersionDropdown.place(relx=0.5, rely=0.6, anchor="center")
        self.serverModloaderDropdown = ctk.CTkComboBox(self.createServerMenu, width=250, height=45, values=self.modLoaders)
        self.serverModloaderDropdown.place(relx=0.5, rely=0.8, anchor="center")
        self.createServerButton = ctk.CTkButton(self.createServerMenu, width=450, text="Create", command=lambda: self.createServer(self.nameInput.get(), self.serverVersionDropdown.get(), self.serverModloaderDropdown.get(), self.wamInput.get()))
        self.createServerButton.place(relx=0.5, rely=0.95, anchor="center")

    def createServer(self, name, version, modloader, ram):
        for object in self.versionManifest["versions"]:
            if object["id"] == version:
                version_dic = self.url_to_dic(object["url"])
        java = version_dic["javaVersion"]["majorVersion"]
        if os.path.exists(os.path.join(SERVERS, name)):
            self.createServerStatusText.configure(text="Server already exists!")
        else:
            os.mkdir(os.path.join(SERVERS, name))
        if name == "":
            self.createServerStatusText.configure(text="Not Valid: Name")
        if not ram.isnumeric():
            self.createServerStatusText.configure(text="Not Valid: RAM")
        if not version in self.versions:
            self.createServerStatusText.configure(text="Not Valid: Version")
        if not modloader in self.modLoader:
            self.createServerStatusText.configure(text="Not Valid: Modloader")
        if os.path.exists(os.path.join(SERVERS, name)) and not name == "" and ram.isnumeric() and version in self.versions and modloader in self.modLoaders:
            gyrosclientJson = {
                        "version" : version,
                        "modloader" : modloader,
                        "ram" : ram,
                        "java" : java
                    }
            with open(os.path.join(SERVERS, name, "gyrosclient.json"), "w") as f:
                json.dump(gyrosclientJson, f, indent=4)
            with open(os.path.join(SERVERS, name, "eula.txt"), "w") as f:
                f.write("eula=true")
            self.updateServers()
            self.createServerMenu.destroy()

    def createProfile(self, name, modloader, version, ram):
        print(os.path.exists(os.path.join(PROFILES, name)))
        if os.path.exists(os.path.join(PROFILES, name)):
            self.createProfileStatusText.configure(text="Profile already exists!")
        else:
            os.mkdir(os.path.join(PROFILES, name))
        if name == "":
            self.createProfileStatusText.configure(text="Not valid: Name")
        if not ram.isnumeric():
            self.createProfileStatusText.configure(text="Not valid: RAM")
        if not version in self.versions:
            self.createProfileStatusText.configure(text="Not valid: Version")
        if not modloader in self.modLoader:
            self.createProfileStatusText.configure(text="Not valid: Modloader")
        
        if ram.isnumeric() and version in self.versions and not name == "" and not os.path.exists(os.path.join(PROFILES, name)) and modloader in self.modLoader:
            json_data = {
                    "name": name,
                    "modloader": modloader,
                    "version": version,
                    "ram": ram
                    }
            with open(os.path.join(PROFILES, name, f"{name}-gyrosClient.json"), "w") as f:
                json.dump(json_data, f, indent=4)
            self.closeProfileMenu()
            self.updateProfiles()
            

    def updateProfiles(self):
        self.sideBar.update()
        elements = os.listdir(PROFILES)
        temp = []
        for element in elements:
            if os.path.isdir(os.path.join(PROFILES, element)):
                temp.append(os.path.join(PROFILES, element))
        self.profiles = temp
        for frame in self.profileFrames:
            frame.destroy()
        for profile in self.profiles:
            frame = ctk.CTkFrame(self.sideBar, width=140, height=90, fg_color="gray10")
            frame.pack(pady=5)
            profileNameText = ctk.CTkLabel(frame, text=os.path.basename(profile), font=("Bold", 14))
            profileNameText.place(x=70, y=30, anchor="center")
            button = ctk.CTkButton(frame, text="Select Profile", width=120, command=lambda profile=profile: self.setProfile(profile))
            button.place(x=10, y=55)
            self.profileFrames.append(frame)
    def vanillaDownload(self, continueFunc):
        for version in self.versionManifest["versions"]:
            if version["id"] == self.version:
                version_dic = self.url_to_dic(version["url"])
                break
        downloadPath = os.path.join(RESOURCES, "versions", self.version)
        os.makedirs(downloadPath, exist_ok=True)
        for lib in version_dic["libraries"]:
            folders = lib["downloads"]["artifact"]["path"].split(sep="/")
            path = ""
            for folder in folders:
                path = os.path.join(path, folder)
            if not os.path.exists(os.path.join(RESOURCES, "libraries", path)):
                self.url_to_file(lib["downloads"]["artifact"]["url"], os.path.abspath(os.path.join(RESOURCES, "libraries", lib["downloads"]["artifact"]["path"])))
        assets_dic = self.url_to_dic(version_dic["assetIndex"]["url"])
        self.futures.append(self.pool.submit(self.downloadAssets, assets_dic))
        os.makedirs(os.path.join(RESOURCES, "assets", "indexes"), exist_ok=True)
        with open(os.path.join(RESOURCES, "assets", "indexes", f"{version_dic["assetIndex"]["id"]}.json"), "w") as f:
            json.dump(self.url_to_dic(version_dic["assetIndex"]["url"]), f, indent=4)
        if not os.path.exists(os.path.join(downloadPath, f"{self.version}.jar")):
            self.url_to_file(version_dic["downloads"]["client"]["url"], os.path.join(downloadPath, f"{self.version}.jar"))
        if not os.path.exists(os.path.join(f"{self.version}.json")):
            self.dic_to_json(version_dic, os.path.join(RESOURCES, "versions", self.version, f"{self.version}.json"))
        threading.Thread(target=continueFunc).start()
    def downloadAssets(self, assets_dic):
        for assetKey in assets_dic["objects"]:
            asset = assets_dic["objects"][assetKey]
            hash = asset["hash"]
            assetPath = os.path.join(RESOURCES, "assets", "objects", hash[:2])
            if not os.path.exists(os.path.join(assetPath, hash)):
                os.makedirs(assetPath, exist_ok=True)
                self.url_to_file(f"{MINECRAFT_BASE_ASSET_URL}{hash[:2]}/{hash}", os.path.join(assetPath, hash))
    def fabricDownload(self, continueFunc):
        url = f"https://meta.fabricmc.net/v2/versions/loader/{self.version}"
        fabricVersionJson = self.url_to_dic(url)[0]
        fabricloaderpath = self.maven_to_file_path(os.path.join(RESOURCES, "libraries"), fabricVersionJson["loader"]["maven"])
        if not os.path.exists(fabricloaderpath):
            self.url_to_file(self.maven_to_url(BASE_FABRIC_URL, fabricVersionJson["loader"]["maven"]), fabricloaderpath)
        for lib in fabricVersionJson["launcherMeta"]["libraries"]["common"]:
            path = self.maven_to_file_path(os.path.join(RESOURCES, "libraries"), lib["name"])
            if not os.path.exists(path):
                self.url_to_file(self.maven_to_url(lib["url"], lib["name"]), path)
        fabricVersionsPath = os.path.join(RESOURCES, "versions", f"fabric-{self.version}")
        if not os.path.exists(fabricVersionsPath):
            os.mkdir(fabricVersionsPath)
            with open(os.path.join(fabricVersionsPath, f"fabric-{self.version}.json"), "w") as f:
                json.dump(fabricVersionJson, f, indent=4)
        continueFunc()

    def playButton_callback(self):
        threading.Thread(target=self.startClient).start()

    def maven_to_url(self, baseURL, maven):
        group, artifact, version = maven.split(sep=":")
        return f"{baseURL.rstrip("/")}/{group.replace(".", "/")}/{artifact}/{version}/{artifact}-{version}.jar"
    
    def maven_to_file_path(self, basePath, maven):
        group, artifact, version = maven.split(sep=":")
        return os.path.join(basePath, group.replace(".", "\\"), artifact, version, f"{artifact}-{version}.jar")

    def stopClient(self):
        if self.clientProccess is not None:
            self.clientProccess.kill()

    def startClient(self):
        self.playButtton.configure(text=f"Stop: {os.path.basename(self.profile)}", fg_color="red", hover_color="#7B2320", command=self.stopClient)
        if not os.path.exists(RESOURCES):
            os.mkdir(RESOURCES)
            os.mkdir(os.path.join(RESOURCES, "assets"))
            os.mkdir(os.path.join(RESOURCES, "versions"))
            os.mkdir(os.path.join(RESOURCES, "libraries"))
        if not os.path.exists(os.path.join(PROFILES, "default")):
            exit()
        runclientfunc = lambda: self.runClient("Gyroslord5", self.version, self.modLoader, self.java, self.profile, os.path.join(RESOURCES, "versions"), os.path.join(RESOURCES, "libraries"), os.path.join(RESOURCES, "assets"))
        if self.modLoader == "fabric":
            continueFunction = lambda: self.fabricDownload(runclientfunc)
        else:
            continueFunction = runclientfunc
        self.vanillaDownload(continueFunction)

    def runClient(self, username, version, modLoader, java, profilePath, versionPath, libraries, assetsPath):
        for future in self.futures:
            future.result()
        self.after(0, lambda: self.updateStatusText("Starting Client..."))
        app.after(10000, lambda: self.updateStatusText(""))
        self.client = Client(username, version, modLoader, java, profilePath, versionPath, libraries, assetsPath)
        self.clientProccess = self.client.initClient()
        threading.Thread(target=self.waitForClient).start()

    def waitForClient(self):
        self.clientProccess.wait()
        self.playButtton.configure(text=f"Start: {os.path.basename(self.profile)}", fg_color="#1F538D", hover_color="#1C487A", command=self.playButton_callback)

    def modLoaderDropdown_callback(self, selection):
        self.modLoader = selection
app = App(1200, 700)
app.mainloop()