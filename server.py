import socketserver
from util.request import Request
from util.router import Router
from util.hello_path import hello_path
from util import publicRoutes as pr

class MyTCPHandler(socketserver.BaseRequestHandler):

    def __init__(self, request, client_address, server):
        self.router = Router()
        self.router.add_route("GET", "/hello", hello_path, True)
        # TODO: Add your routes here
        self.router.add_route("GET","/", pr.serveHTML, True)
        self.router.add_route("GET","/chat", pr.serveHTML, True)
        self.router.add_route("GET","/public/js", pr.serveHTML, False)
        self.router.add_route("GET","/public/css", pr.serveCSS, False)
        self.router.add_route("GET","/api/chats", pr.serveChats, True)
        self.router.add_route("POST","/api/chats", pr.addChats, True)
        self.router.add_route("GET","/public/imgs",pr.serveImg, False)
        self.router.add_route("PATCH","/api/chats/", pr.updateChats, False)
        self.router.add_route("DELETE","/api/chats/", pr.deleteChats, False)
        self.router.add_route("GET","/favicon.ico", pr.faviconLoader, True)
        self.router.add_route("GET","/public/",pr.serveHTML,False)
        self.router.add_route("PATCH","/api/reaction/",pr.addEmoji,False)
        self.router.add_route("DELETE","/api/reaction/",pr.removeEmoji,False)
        
        super().__init__(request, client_address, server)

    def handle(self):
        received_data = self.request.recv(2048)
        print(self.client_address)
        print("--- received data ---")
        print(received_data)
        print("--- end of data ---\n\n")
        request = Request(received_data)
    
        self.router.route_request(request, self)


def main():
    host = "0.0.0.0"
    port = 8080
    socketserver.TCPServer.allow_reuse_address = True

    server = socketserver.TCPServer((host, port), MyTCPHandler)

    print("Listening on port " + str(port))
    server.serve_forever()


if __name__ == "__main__":
    main()
