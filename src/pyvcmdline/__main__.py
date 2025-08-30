# pyvcmdline/__main__.py
"""
Command line interface for pyved-engine.
"""
import argparse
import textwrap
from . import subcommand
from .pyvcli_defs import VER_DISP_MSG
from .pyvcli_defs import pe_vars

__version__ = pe_vars.ENGINE_VERSION_STR

# Central help registry (single place to edit copy/structure)
HELP = {
    "global": {
        "usage": "pyv-cli [option] subcommand [subcommand_options]",
        "description": "Command line tool for pyved-engine, used to operate with/manipulate game bundles.",
        "epilog": textwrap.dedent("""\
            Tips:
              • Run `pyv-cli <subcommand> -h` for detailed help and examples of that subcommand.
              • Use `-d/--dev` with `share` to target the developer sandbox.

            Examples:
              pyv-cli init MyNewGame
              pyv-cli play . --host 127.0.0.1 --port 8765 --mode ws
              pyv-cli serve MyServerBundle --host 0.0.0.0 --port 9000
              pyv-cli refresh .
              pyv-cli upgrade MyGame
        """)
    },
    "init": {
        "help": "initialize a new game bundle",
        "description": textwrap.dedent("""\
            Initialize a new game bundle.

            Creates the basic folder structure and metadata to start a project.
        """),
        "epilog": textwrap.dedent("""\
            Examples:
              pyv-cli init MyNewGame
              pyv-cli init mygame
        """)
    },
    "play": {
        "help": "play a given game bundle in the local context",
        "description": textwrap.dedent("""\
            Run a bundle locally (client-side).

            Useful for quick iteration when developing gameplay.
        """),
        "epilog": textwrap.dedent("""\
            Examples:
              pyv-cli play .
              pyv-cli play MyGame --mode ws
              pyv-cli play MyGame --host 127.0.0.1 --port 8765 --player 2
        """)
    },
    "autogen": {
        "help": "for system devs only (=dev tool equivalent to a PyConnector autogen script)",
        "description": "Developer-only tool. Generates code/assets from internal templates.",
        "epilog": None
    },
    "upgrade": {
        "help": "upgrade a game to enable katagames API calls",
        "description": textwrap.dedent("""\
            Upgrade a bundle to enable Katagames/pyved integrations.

            Typical tasks may include:
              • adding or updating integration hooks
              • adjusting bundle metadata
              • preparing files for API calls

            (Exact actions depend on the pyv-cli version you're using)
        """),
        "epilog": textwrap.dedent("""\
            Usage:
              pyv-cli upgrade <bundle_name>

            Examples:
              pyv-cli upgrade .
              pyv-cli upgrade MyGame
        """)
    },
    "refresh": {
        "help": "rescan source/assets and update bundle metadata",
        "description": textwrap.dedent("""\
            Refresh the bundle metadata by scanning source files and assets.

            Useful after adding/removing files so metadata stays in sync.
        """),
        "epilog": textwrap.dedent("""\
            Examples:
              pyv-cli refresh .
              pyv-cli refresh MyGame
        """)
    },
    "bump": {
        "help": "update bundle metadata to mark current pyved-engine revision",
        "description": textwrap.dedent("""\
            Bump the engine revision used by the bundle.

            Records that the bundle targets the current pyved-engine version.
        """),
        "epilog": textwrap.dedent("""\
            Examples:
              pyv-cli bump .
              pyv-cli bump MyGame
        """)
    },
    "serve": {
        "help": "run the server code for a given game bundle",
        "description": textwrap.dedent("""\
            Start the server side for a bundle.

            Forwarded options let you bind host/port and select transport.
        """),
        "epilog": textwrap.dedent("""\
            Examples:
              pyv-cli serve MyServerBundle
              pyv-cli serve MyServerBundle --host 0.0.0.0 --port 9000
              pyv-cli serve . --mode ws
        """)
    },
    "share": {
        "help": "share a given game bundle with the world",
        "description": textwrap.dedent("""\
            Share a bundle (publish or make it accessible as configured).

            Notes:
              • This subcommand accepts the global --dev flag to target the developer server.
        """),
        "epilog": textwrap.dedent("""\
            Examples:
              pyv-cli share .
              pyv-cli --dev share MyGame
        """)
    },
    "test": {
        "help": "validate that a bundle is structurally correct",
        "description": textwrap.dedent("""\
            Run validation checks on a bundle.

            Verifies structure and basic expectations so you can catch issues early.
        """),
        "epilog": textwrap.dedent("""\
            Examples:
              pyv-cli test .
              pyv-cli test MyGame
        """)
    },
    "ts-creation": {
        "help": "create the JSON file that matches a tileset",
        "description": textwrap.dedent("""\
            Create a tileset JSON from a source image.

            Generates a JSON description that matches your tileset sheet.
        """),
        "epilog": textwrap.dedent("""\
            Example:
              pyv-cli ts-creation assets/tileset.png
        """)
    },
    "pub": {
        "help": "request game publication given a sandboxed-share slug",
        "description": textwrap.dedent("""\
            Request publication for an existing game slug (cloud-based storage).

            This assumes the game has already been shared/synced to the sandbox.
        """),
        "epilog": textwrap.dedent("""\
            Example:
              pyv-cli pub my-game-slug
        """)
    }
}

CMD_MAPPING = {
    'autogen': None,
    'bump': subcommand.bump,
    'init': subcommand.init,
    'play': subcommand.play,
    'serve': subcommand.serve,
    'pub': None,
    'refresh': subcommand.refresh,
    'share': subcommand.share,
    'test': subcommand.test,
    'ts-creation': subcommand.ts_creation,
    'upgrade': subcommand.upgrade,
}

# Unified formatter (keeps newlines, shows defaults)
class SmartFormatter(argparse.ArgumentDefaultsHelpFormatter, argparse.RawDescriptionHelpFormatter):
    pass


# TODO the deprecated code below may be useful to implementing a future "repair" bundle subcommand
# def _bundle_renaming(path_to_bundle):
#     # ensure that OUR NORM is respected:
#     # what norm? We need to enforce the rule that states:
#     # the directory name == the slug
#     pass


def trigger_publish(slug):  # deprecated func
    """
    once the game is available server-side, as a stored cartridge,
    (therefore your game has a slug/Server-side game identifier)

    we trigger the "PUBLISH" op server-side.
    This means the game will spawn/pop within the gaming CMS (cloudarcade)

    :param slug: str that the server uses to uniquely identify a cartridge
    stored server-side
    :return: True/False
    """
    raise NotImplementedError


def _remove_junk_from_bundle_name(x):
    """Trim trailing slashes from bundle names."""
    t = x.rstrip('/')
    t = t.rstrip('\\')
    return t

def main_inner(parser, argns):
    """Dispatch selected subcommand."""
    no_arg_subcommands = {'autogen'}
    extra_flags_subcommands = {'share'}
    ope_name = argns.subcommand

    if argns.version:
        print(VER_DISP_MSG % __version__)
        return 0
    if argns.help:
        parser.print_help()
        return 0
    if ope_name not in CMD_MAPPING:
        parser.print_help()
        return 1
    if CMD_MAPPING[ope_name] is None:
        raise NotImplementedError(f"subcommand \"{ope_name}\" is valid, but isnt implemented yet!")

    adhoc_subcommand_func = CMD_MAPPING[ope_name]

    if ope_name in no_arg_subcommands:
        adhoc_subcommand_func()
    elif ope_name in ('play', 'serve'):
        kwargs = {k: v for k, v in vars(argns).items() if k not in ["bundle_name", "command"] and v is not None}
        xarg = _remove_junk_from_bundle_name(argns.bundle_name)
        adhoc_subcommand_func(xarg, **kwargs)
    elif ope_name == 'ts-creation':
        adhoc_subcommand_func(argns.image_path)
    else:
        xarg = _remove_junk_from_bundle_name(argns.bundle_name)
        if ope_name in extra_flags_subcommands:
            adhoc_subcommand_func(xarg, argns.dev)
        else:
            adhoc_subcommand_func(xarg)
    return 0


def do_parse_args():
    """Build CLI and parse arguments."""
    parser = argparse.ArgumentParser(
        description=HELP["global"]["description"],
        add_help=False,
        usage=HELP["global"]["usage"],
        formatter_class=SmartFormatter,
        epilog=HELP["global"]["epilog"]
    )

    # Global options (mutually exclusive to preserve retro-compatibility)
    special_modes_group = parser.add_argument_group('Options')
    either_one_option = special_modes_group.add_mutually_exclusive_group()
    either_one_option.add_argument('-v', '--version', action='store_true', help='Print the current pyved engine version.')
    either_one_option.add_argument('-h', '--help', action='store_true', help='Print this help.')
    either_one_option.add_argument('-d', '--dev', action='store_true', help='Use the developer server (tool debug etc)')

    # Subcommands group
    subparsers = parser.add_subparsers(title="Subcommands", dest="subcommand", required=False, metavar="subcommand")

    # init
    init_parser = subparsers.add_parser(
        "init",
        help=HELP["init"]["help"],
        formatter_class=SmartFormatter,
        description=HELP["init"]["description"],
        epilog=HELP["init"]["epilog"]
    )
    init_parser.add_argument("bundle_name", type=str, help="Name of the bundle")

    # play
    play_parser = subparsers.add_parser(
        "play",
        help=HELP["play"]["help"],
        formatter_class=SmartFormatter,
        description=HELP["play"]["description"],
        epilog=HELP["play"]["epilog"]
    )
    play_parser.add_argument("bundle_name", type=str, nargs="?", default=".", help="Specified bundle (default: current folder)")
    play_parser.add_argument("--host", type=str, help="Server hostname")
    play_parser.add_argument("--port", type=int, help="Server port")
    play_parser.add_argument("--player", type=int, help="local player identifier")
    play_parser.add_argument("--mode", type=str, help="what type of transport layer to use (ws/socket/etc)")

    # autogen
    autogen = subparsers.add_parser(
        "autogen",
        help=HELP["autogen"]["help"],
        formatter_class=SmartFormatter,
        description=HELP["autogen"]["description"],
        epilog=HELP["autogen"]["epilog"]
    )

    # upgrade
    play_parser = subparsers.add_parser(
        "upgrade",
        help=HELP["upgrade"]["help"],
        formatter_class=SmartFormatter,
        description=HELP["upgrade"]["description"],
        epilog=HELP["upgrade"]["epilog"]
    )
    play_parser.add_argument("bundle_name", type=str, help="Specified bundle")

    # refresh
    play_parser = subparsers.add_parser(
        "refresh",
        help=HELP["refresh"]["help"],
        formatter_class=SmartFormatter,
        description=HELP["refresh"]["description"],
        epilog=HELP["refresh"]["epilog"]
    )
    play_parser.add_argument("bundle_name", type=str)

    # bump
    play_parser = subparsers.add_parser(
        "bump",
        help=HELP["bump"]["help"],
        formatter_class=SmartFormatter,
        description=HELP["bump"]["description"],
        epilog=HELP["bump"]["epilog"]
    )
    play_parser.add_argument("bundle_name", type=str)

    # serve
    serve_parser = subparsers.add_parser(
        "serve",
        help=HELP["serve"]["help"],
        formatter_class=SmartFormatter,
        description=HELP["serve"]["description"],
        epilog=HELP["serve"]["epilog"]
    )
    serve_parser.add_argument("bundle_name", type=str, help="Specified bundle (default: current folder)")
    serve_parser.add_argument("--host", type=str, help="Server hostname")
    serve_parser.add_argument("--port", type=int, help="Server port")
    serve_parser.add_argument("--player", type=int, help="local player identifier")
    serve_parser.add_argument("--mode", type=str, help="what type of transport layer to use (ws/socket/etc)")

    # share
    share_parser = subparsers.add_parser(
        "share",
        help=HELP["share"]["help"],
        formatter_class=SmartFormatter,
        description=HELP["share"]["description"],
        epilog=HELP["share"]["epilog"]
    )
    share_parser.add_argument("bundle_name", type=str, nargs="?", default=".", help="Specified bundle (default: current folder)")

    # test
    play_parser = subparsers.add_parser(
        "test",
        help=HELP["test"]["help"],
        formatter_class=SmartFormatter,
        description=HELP["test"]["description"],
        epilog=HELP["test"]["epilog"]
    )
    play_parser.add_argument("bundle_name", type=str)

    # ts-creation
    tsc_parser = subparsers.add_parser(
        "ts-creation",
        help=HELP["ts-creation"]["help"],
        formatter_class=SmartFormatter,
        description=HELP["ts-creation"]["description"],
        epilog=HELP["ts-creation"]["epilog"]
    )
    tsc_parser.add_argument("image_path", type=str)

    # pub
    pubpp = subparsers.add_parser(
        "pub",
        help=HELP["pub"]["help"],
        formatter_class=SmartFormatter,
        description=HELP["pub"]["description"],
        epilog=HELP["pub"]["epilog"]
    )
    pubpp.add_argument("slug", type=str, help="existing game slug (=identifier in the cloud-based storage)")

    ret_args = parser.parse_args()
    main_inner(parser, ret_args)


if __name__ == '__main__':
    do_parse_args()
