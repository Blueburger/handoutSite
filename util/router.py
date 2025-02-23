
class Router:

    def __init__(self):
        # Initialize list to store routes in
        self.routes = []

    def add_route(self, method, path, action, exact_path=False):
        # for adding route to route list
        self.routes.append((path, method, action, exact_path))


    def route_request(self,request,handler):
        path = request.path
        method = request.method
        matched = None
        for rPath, rMeth, funct, exact in self.routes:
            if exact and rPath == path and rMeth == method:
                matched = funct
                break
            if not exact and path.startswith(rPath) and rMeth == method and matched is None:
                matched = funct
        if matched:
            matched(request, handler)
        else:
            handler.request.sendall("HTTP/1.1 404 Not Found\r\nX-Content-Type-Options: nosniff\r\nContent-Type: text/plain\r\nContent-Length: 55\r\n\r\nRouter Says The Page you are looking for does not exist".encode())

    