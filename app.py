from http.server import BaseHTTPRequestHandler, HTTPServer
import json

class MyServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        response = {"status": "Success", "message": "Greetings from Pulumi and 3-Tier APP. It is working properly."}
        self.wfile.write(bytes(json.dumps(response), "utf-8"))

if __name__ == "__main__":
    webServer = HTTPServer(("0.0.0.0", 5000), MyServer)
    print("Server started on port 5000")
    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass
    webServer.server_close()