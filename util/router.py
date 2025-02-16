
class Router:

    def __init__(self):
        # Initialize list to store routes in
        self.routes = []

    def add_route(self, method, path, action, exact_path=False):
        # for adding route to route list
        self.routes.append((path, method, action, exact_path))

    def route_request(self, request, handler):
        path = request.path
        method = request.method
        print(f'the router is deciding where to route: {path} with method: {method}')
        for rouPack in self.routes:
            rPath = rouPack[0]
            rMeth = rouPack[1]
            funct = rouPack[2]
            exact = rouPack[3]
            
            
            if exact:
                #print("is an exact path")
                if rPath == path and rMeth == method:
                    print(f'exact path chosen: {funct}')
                    return funct(request, handler)
            print(f"is path: {path}  in rPath: {rPath}\n\nmethod: {method}")
            if not exact and rPath in path and rMeth == method:
                print(f'response chosen first: {funct}')
                return funct(request, handler)
            
            
            
        # should return a 404 page not found error, place holder string return    
        #return handler.request.sendall("HTTP/1.1 404 notFound\r\nX-ContentTypeOptions: nosniff\r\nContent-Type: text/plain\r\nContent-Length: 43\r\n\r\nThe Page you are looking for does not exist".encode())
        return 404