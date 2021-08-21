from .app import run_app
import argparse
import pathlib
import asyncio


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "directory",
        default=".",
        type=pathlib.Path,
        help="base path to serve files from",
    )
    parser.add_argument(
        "-b", "--host", default="localhost", help="IP address to server from"
    )
    parser.add_argument("-p", "--port", default=8080, help="port to serve from")
    parser.add_argument(
        "-f", "--frequency", default=360, help="poll frequency (per minute)"
    )
    args = parser.parse_args(args=argv)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(
        run_app(args.directory, args.host, args.port, 60 / args.frequency)
    )


if __name__ == "__main__":
    main()
