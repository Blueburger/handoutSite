import re
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
        for pattern in self.routes:
            match = re.match(pattern[0], path)
            if match and method == pattern[1]:
                funct = pattern[2]
                return funct(request, handler)
        # should return a 404 page not found error, place holder string return    
        return "error"
