import minecraft_launcher_lib
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

CLIENT_ID = "abab9706-d135-475a-8e1c-156a1fdaf8f5"
# Für öffentliche Desktop-Clients/Localhost bleibt das Secret bei der Lib oft leer oder None
CLIENT_SECRET = None  
REDIRECT_URL = "http://localhost:8000"

# 1. Login-URL generieren
login_url = minecraft_launcher_lib.microsoft_account.get_login_url(CLIENT_ID, REDIRECT_URL)

print("Öffne Browser für den Microsoft-Login...")
webbrowser.open(login_url)

# 2. Lokaler Server, um den ?code= abzufangen
auth_code = None

class TokenHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        global auth_code
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        
        query = urlparse(self.path).query
        params = parse_qs(query)
        
        if "code" in params:
            auth_code = params["code"][0]
            self.wfile.write(b"<h1>Login erfolgreich!</h1><p>Du kannst dieses Fenster jetzt schliessen.</p>")
        else:
            self.wfile.write(b"<h1>Fehler</h1><p>Kein Code empfangen.</p>")

# Server starten und auf den Redirect von Microsoft warten
server = HTTPServer(("localhost", 8000), TokenHandler)
print("Warte auf Antwort von Microsoft auf Port 8000...")
server.handle_request() # Stoppt, sobald ein Request reinkommt
server.server_close()

# 3. Den Login abschließen (Der kritische Punkt)
if auth_code:
    try:
        print("Tausche Microsoft-Code gegen Minecraft-Token aus...")
        login_data = minecraft_launcher_lib.microsoft_account.complete_login(
            CLIENT_ID, CLIENT_SECRET, REDIRECT_URL, auth_code
        )
        
        print("ERFOLG! Minecraft-Token erhalten.")
        print(f"Spielername: {login_data['name']}")
        
    except minecraft_launcher_lib.microsoft_account.AzureAppNotPermitted:
        print("\n❌ FEHLER: AzureAppNotPermitted")
        print("Deine Azure App funktioniert technisch perfekt! Aber Microsoft blockiert dich.")
        print("Du MUSST das Formular ausfüllen: https://aka.ms")
        print("Erst nach der manuellen Mojang-Freischaltung (3-4 Wochen) klappt dieser Schritt.")
        
    except Exception as e:
        print(f"\n❌ Anderer Fehler aufgetreten: {e}")
