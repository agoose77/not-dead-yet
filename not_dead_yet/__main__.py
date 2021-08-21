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
    parser.add_argument(
        "-b", "--host", default="localhost", help="IP address to serve from"
    )
    parser.add_argument("-p", "--port", default=8080, help="port to serve from")
    parser.add_argument(
        "-l", "--listener", default=9000, help="port to listen for reload commands"
    )
    parser.add_argument(
        "-f", "--frequency", default=360, help="poll frequency (per minute)"
    )
    parser.add_argument(
        "-i", "--ignore", action="append", help="glob pattern to ignore", default=[".*"]
    )
    parser.add_argument("--no-watch", action="store_true", help="don't watch files")


def handle_serve_args(args):
    loop = asyncio.get_event_loop()
    loop.run_until_complete(
        run_static_server(
            args.directory,
            host=args.host,
            port=args.port,
            dt=60 / args.frequency,
            ignore_patterns=args.ignore,
            listener_port=args.listener,
            watch_files=not args.no_watch,
        )
    )


def setup_reload_command(parser):
    pass


def handle_reload_args(args):
    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.open_connection(args.host, args.listener))


def main(argv=None):
    parser = argparse.ArgumentParser()

    # Shared parameters
    parser.add_argument("-b", "--host", default="localhost", help="host IP address")
    parser.add_argument("-l", "--listener", default=9000, help="control port")

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
