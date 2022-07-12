from .serve import run_static_server
import argparse
import pathlib
import asyncio



def setup_serve_command(parser):
    parser.add_argument(
        "directory",
        default=".",
        type=pathlib.Path,
        help="base path to serve files from",
    )
    parser.add_argument("-p", "--port", type=int, default=8080, help="port to serve from")
    parser.add_argument(
        "-f", "--frequency", default=360, type=int, help="poll frequency (per minute)"
    )
    parser.add_argument(
        "-i", "--ignore", action="append", help="glob pattern to ignore", default=[".*"]
    )
    parser.add_argument("--no-watch", action="store_true", help="don't watch files")
    parser.add_argument("-b", "--host", default="localhost", help="host IP address")
    parser.add_argument("-c", "--control", type=int, default=9000, help="control port")


def handle_serve_args(args):
    loop = asyncio.get_event_loop()
    loop.run_until_complete(
        run_static_server(
            args.directory,
            host=args.host,
            port=args.port,
            dt=60 / args.frequency,
            ignore_patterns=args.ignore,
            control_port=args.control,
            watch_files=not args.no_watch,
        )
    )


def setup_reload_command(parser):
    parser.add_argument("-b", "--host", default="localhost", help="host IP address")
    parser.add_argument("-c", "--control", type=int, default=9000, help="control port")


def handle_reload_args(args):
    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.open_connection(args.host, args.control))


def main(argv=None):
    parser = argparse.ArgumentParser()

    subparsers = parser.add_subparsers()
    reload_parser = subparsers.add_parser("reload")
    setup_reload_command(reload_parser)
    reload_parser.set_defaults(handler=handle_reload_args)

    serve_parser = subparsers.add_parser("serve")
    setup_serve_command(serve_parser)
    serve_parser.set_defaults(handler=handle_serve_args)

    args = parser.parse_args(args=argv)
    if "handler" in args:
        args.handler(args)


if __name__ == "__main__":
    main()
