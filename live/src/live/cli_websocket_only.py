# system import
import argparse

# custom import
from observer_live_api import SmartWebSocketV2Client, AlertObserver, MongoDBObserver

def run_command(args):
    """ Run Mongo Db server locally/cloud"""
    _mdb = MongoDBObserver()
    # check if is running
    if not _mdb.is_mongodb_running():
        print('+++ Run MongoDb Server')
        _mdb.start_mongodb()

def start_command(args):
    """Handles the 'start' command"""
    print(f"Starting WebSocket with max_retries={args.max_retries} and log_level={args.log_level}")
    smartWebSocketObject = SmartWebSocketV2Client()
    smartWebSocketObject.start()

def stop_command(args):
    """Handles the 'stop' command"""
    print("Stopping WebSocket connection...")

def restart_command(args):
    """Handles the 'restart' command"""
    print(f"Restarting WebSocket with delay={args.delay} seconds")

def create_parser():
    """Creates the argument parser with subcommands."""
    parser = argparse.ArgumentParser(description="WebSocket CLI Controller")
    subparsers = parser.add_subparsers(dest='command', required=True, help="Available commands")

    # 'start' command
    parser_start = subparsers.add_parser('start', help="Start the WebSocket connection")
    parser_start.add_argument('--max-retries', type=int, default=3, help="Maximum number of reconnection attempts")
    parser_start.add_argument('--log-level', type=str, choices=['debug', 'info', 'warning', 'error'], default='info',
                              help="Set the logging level")
    parser_start.set_defaults(func=start_command)

    # 'stop' command
    parser_stop = subparsers.add_parser('stop', help="Stop the WebSocket connection")
    parser_stop.set_defaults(func=stop_command)

    # 'restart' command
    parser_restart = subparsers.add_parser('restart', help="Restart the WebSocket connection")
    parser_restart.add_argument('--delay', type=int, default=5, help="Delay before restarting (in seconds)")
    parser_restart.set_defaults(func=restart_command)

    # 'runmongodb' command
    parser_run = subparsers.add_parser('runmongo', help="Start Mongo DB server")
    parser_run.set_defaults(func=run_command)
    return parser

def main(args=None):
    """Parses command-line arguments and executes the appropriate command."""
    parser = create_parser()
    args = parser.parse_args(args)
    args.func(args)  # Call the associated function

if __name__ == "__main__":
    main()
