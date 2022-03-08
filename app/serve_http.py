from http.server import HTTPServer, SimpleHTTPRequestHandler


def serve_http(path=None, server_class=HTTPServer, handler_class=SimpleHTTPRequestHandler,
               url="http://localhost", port=8000):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    if path:
        nodes_path = path / "nodes.csv"
        edges_path = path / "edges.csv"
        params = "nodes={}&edges={}".format(nodes_path.as_posix(), edges_path.as_posix())
    else:
        params = ""
    print("Serving HTTP at {}:{}?{}".format(url, port, params))
    httpd.serve_forever()
