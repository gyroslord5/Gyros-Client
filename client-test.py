import subprocess
import os
APPDATA = os.getenv("APPDATA")
MINECRAFT = os.path.join(APPDATA, ".minecraft")
LIBRARIES = os.path.join(MINECRAFT, "libraries", "*")
command = ["java",
            "-Xms2G",
              "-Xmx4G",
                "-XX:+UseG1GC",
                  f"-Djava.library.path={MINECRAFT}\bin",
                    "-cp",
                      f"{LIBRARIES};{os.path.join(MINECRAFT,"versions","26.1.2", "26.1.2.jar")}",
                        "net.minecraft.client.main.Main",
                            "--version",
                                "26.1.2",
                                 "--versionType",
                                    "release",
                                        "--accessToken",
                                            "0",
                                                "--username",
                                                    "Gyroslord5",
                                                        "--uuid",
                                                            "d6131ecd-caad-4049-a88e-76ad2cab490f"]
subprocess.run(command)