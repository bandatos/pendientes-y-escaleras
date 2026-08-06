import requests
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse

# Configuración

url = "https://api.miro.com/v2/oauth-token"

headers = {"accept": "application/json"}

response = requests.get(url, headers=headers)

print(response.text)
CLIENT_ID = "3458764657415994108"
CLIENT_SECRET = "tu_client_secret"
REDIRECT_URI = "http://localhost:8000/callback"
ACCESS_TOKEN = "eyJtaXJvLm9yaWdpbiI6ImV1MDEifQ_iE_XXyAtX2ONg_AlhzviAvnJte0"


auth_url  = (
    f"https://miro.com/oauth/authorize?response_type=code"
    f"&client_id={CLIENT_ID}"
    f"&redirect_uri={REDIRECT_URI}"
    # f"&state={optional_state_value}"
    # f"&team_id={optional_team_id_value}"
)
#
#
# # Paso 2: Capturar el código de autorización
# class CallbackHandler(BaseHTTPRequestHandler):
#     def do_GET(self):
#         query = urllib.parse.urlparse(self.path).query
#         params = urllib.parse.parse_qs(query)
#
#         if 'code' in params:
#             self.server.auth_code = params['code'][0]
#             self.send_response(200)
#             self.end_headers()
#             self.wfile.write(b"Autenticacion exitosa! Puedes cerrar esta ventana.")
#
#     def log_message(self, format, *args):
#         pass
#
#
# server = HTTPServer(('localhost', 8000), CallbackHandler)
# server.handle_request()
# auth_code = server.auth_code
#
#
# # Paso 3: Intercambiar código por access token
# token_url = "https://api.miro.com/v1/oauth/token"
# data = {
#     "grant_type": "authorization_code",
#     "client_id": CLIENT_ID,
#     "client_secret": CLIENT_SECRET,
#     "code": auth_code,
#     "redirect_uri": REDIRECT_URI
# }
#
#
# response = requests.post(token_url, data=data)
# access_token = response.json()["access_token"]
# print(f"Access Token obtenido: {access_token}")
