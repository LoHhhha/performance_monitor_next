import argparse
import atexit
from http.server import ThreadingHTTPServer

from .combiner import Combiner
from .handler import MetricsHandler


if __name__ == "__main__":
    arguments = argparse.ArgumentParser()
    arguments.add_argument("-p", "--port", type=int, default=54321)
    arguments.add_argument("--host", type=str, default="127.0.0.1")
    arguments.add_argument("--path", type=str, default="/info")
    args = arguments.parse_args()

    combiner = Combiner()
    atexit.register(combiner.dispose)
    path = args.path if args.path.startswith("/") else f"/{args.path}"

    MetricsHandler.combiner = combiner
    MetricsHandler.endpoint_path = path

    server = ThreadingHTTPServer((args.host, args.port), MetricsHandler)
    atexit.register(server.server_close)

    print(f"Serving POST {path} at http://{args.host}:{args.port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.shutdown()
        server.server_close()
