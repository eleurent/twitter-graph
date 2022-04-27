from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from typing import Tuple


def serve_http(path: Path = None, server_class: HTTPServer = HTTPServer,
               handler_class: SimpleHTTPRequestHandler = SimpleHTTPRequestHandler,
               url: str = "http://localhost", port: int = 8000):
    server_address: Tuple[str, int] = ('', port)
    httpd = server_class(server_address, handler_class)
    if path:
        nodes_path: Path = path / "nodes.csv"
        edges_path: Path = path / "edges.csv"
        params: str = f'nodes={nodes_path.as_posix()}&edges={edges_path.as_posix()}'
    else:
        params = ''
    print(f'Serving HTTP at {url}:{port}?{params}')
    httpd.serve_forever()


if __name__ == "__main__":
    serve_http(Path('/out/juan_m12i'))
