from beets.plugins import BeetsPlugin
from beets.ui import Subcommand


def say_hi(lib, opts, args):
    print("Hello everybody! I'm a plugin!")


class MapTagPlugin(BeetsPlugin):
    def commands(self):
        command = Subcommand("maptag", help="test")
        command.func = say_hi
        return [command]
