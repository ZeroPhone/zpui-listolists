from zpui_lib.helpers import setup_logger, local_path_gen, read_or_create_config, save_config_method_gen
from zpui_lib.ui import PrettyPrinter as Printer, Menu, UniversalInput
from zpui_lib.apps import ZeroApp

local_path = local_path_gen(__name__)
logger = setup_logger(__name__, "info")

module_path = "personal/" # app path, needed to place your app in a correct menu directory
# for app directory paths, see https://github.com/ZeroPhone/ZPUI/tree/master/apps
# (do check that the directory you're using, isn't an app)

default_config = """app_name: List o' lists
lists:
  - name: List one
    entries:
     - First entry
     - Second entry
     - Third entry
  - name: List two
    entries:
     - First entry 2
     - Second entry 2
     - Third entry 2
"""

class App(ZeroApp):
    menu_name = "List o' lists" # App name as seen in main menu while using the system
    config_filename = "config.yaml"

    def init_app(self):
        # this is where you put commands that need to run when ZPUI loads
        # if you want to do something long-winded here, consider using BackgroundRunner!
        # feel free to completely remove this function if it's not used
        self.config = read_or_create_config(local_path(self.config_filename), default_config, self.menu_name+" app")
        logger.info(f"Our config looks like this: {self.config}")
        self.save_config = save_config_method_gen(self, local_path(self.config_filename))
        self.menu_name = self.config.get("app_name", self.menu_name) # now the app can be renamed from the config file

    def can_load(self):
        # this function is called to determine whether the app is able to run on this instance of ZPUI.
        # for instance, here's how you can avoid loading the app if the screen dimensions are lower than 320x240:
        #
        #if self.o.width < 320 or self.o.height < 240:
        #    return False, "app requires at least 320x240 screen"
        #
        # If the app can be loaded, `return True`.
        # If the app cannot be loaded, `return (False, reason)`, where `reason` is a human-readable string describing why the app cannot be loaded.
        # NOTE: currently, `can_load()` is not supported in ZPUI for external apps, but it will be supported soon.
        return True

    def settings_menu(self):
        mc = [["Edit names", self.edit_names]]
        Menu(mc, self.i, self.o, name=self.menu_name+" settings menu").activate()

    def edit_names(self):
        mc = []
        for index, list in enumerate(self.config["lists"]):
            mc.append([list.get("name", "List name missing!"), lambda x=index: self.edit_name(x)])
        Menu(mc, self.i, self.o, name=self.menu_name+" name edit menu").activate()

    def edit_name(self, index):
        current_name = self.config["lists"][index].get("name", "")
        name = UniversalInput(self.i, self.o, value=current_name, message="List name:", name=f"List {index} ({current_name}) name input").activate()
        if name:
            self.config["lists"][index]["name"] = name
            self.save_config()

    def list_menu(self, list):
        Printer(f"List {list}", self.i, self.o, 2)

    def on_start(self):
        """This function is called when you click on the app in the main menu"""
        mc = []
        for list in self.config["lists"]:
            mc.append([list.get("name", "List name missing!"), lambda x=list: self.list_menu(x)])
        mc.append(["Settings", self.settings_menu])
        m = Menu(mc, self.i, self.o, name=self.menu_name+" main menu")
        logger.info("menu is starting yay")
        m.activate()
        logger.info("menu has exited yay")



################################################
#
# remember - if you're stuck building something,
# ask me all the questions!
# I'm here to try and help you.
#
################################################


"""
TESTS

Here you can test your app's features or sub-features.
"""

class TestedApp(App):
    """
    A stubbed version of the app, so that internal functions can be tested without substituting a lot of ZPUI input/output code.
    """
    def __init__(self):
        pass # makes sure the app doesn't have to be initialized
    # substitute other functions here as needed for testing

import unittest
class Tests(unittest.TestCase):
    def test_simple(self):
        """Simple test. Checks if the app's get_text function actually returns text."""
        app = TestedApp()
        # feel free to do any further substitutions here.
        #assert isinstance(app.get_text(), str)

if __name__ == "__main__":
    print("Warning: running this app directly will not make it launch. See the README for installation instructions.\n")
    print("Now, running tests:")
    unittest.main()

