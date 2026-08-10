import os
import shutil
import ctypes
APPDATA = os.environ["APPDATA"]
APPDATA_INSTALL = os.path.join(APPDATA, "GyrosClient")
PROGRAMS_INSTALL = "c:\\Program Files\\Gyros Client"
SHORTCUT = "c:\\ProgramData\\Microsoft\\Windows\\Start Menu\\Programs\\Gyros Client.lnk"
if ctypes.windll.shell32.IsUserAnAdmin():
    print("Are you sure everything including mods, savefiles, resourcepacks and more will be gone")
    choice = input("[Y/N]: ")
    done = False
    while not done:
        if choice.lower() == "y":
            print("[LOG] Starting uninstall...")
            if os.path.exists(APPDATA_INSTALL):
                print("[LOG] Removing "+APPDATA_INSTALL)
                shutil.rmtree(APPDATA_INSTALL)
            if os.path.exists(PROGRAMS_INSTALL):
                print("[LOG] Removing "+PROGRAMS_INSTALL)
                shutil.rmtree(PROGRAMS_INSTALL)
            if os.path.exists(SHORTCUT):
                print("[LOG] Removing "+SHORTCUT)
                os.remove(SHORTCUT)
            if os.path.exists(os.path.join(APPDATA_INSTALL, "Servers")):
                print("[LOG] Removing "+os.path.join(APPDATA_INSTALL, "Servers"))
                shutil.rmtree(os.path.join(APPDATA_INSTALL, "Servers"))
            print("Uninstall Done!")
            done = True
        elif choice.lower() == "n":
            exit()
        else:
            print("Please input something valid")
else:
    print("You have to run this program with admin rights")
input("Press enter to exit...")