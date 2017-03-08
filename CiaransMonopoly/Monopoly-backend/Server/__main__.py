from sys import exit, stderr
from argparse import ArgumentParser
try:
    from .Server import Server
except SystemError:
    stderr.write("Monopoly.Server [ERROR]: Server must be run as a module. Check the README for instructions")
    exit(1)

"""
Allows for running the code using python3 -m Server
"""

parser = ArgumentParser(
    prog="Monopoly.Server",
    usage="python3 -m Server [-h] [-t]",
    description="%(prog)s: Server of the Monopoly game written by Super Confused"
)
parser.add_argument(
    '-t', '--test',
    help='Runs a test of the server',
    action='store_true',
)

# Set up a Server instance
args = parser.parse_args()
if args.test:
    from .TestClient import run_test
    run_test()
else:
    server = Server()

    # Allow for Keyboard interrupts
    try:
        server.serve()
    except KeyboardInterrupt:
        server.close()

