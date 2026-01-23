from zpui_lib.helpers import setup_logger, local_path_gen
from zpui_lib.ui import PrettyPrinter as Printer, Menu
from zpui_lib.apps import ZeroApp

local_path = local_path_gen(__name__)
logger = setup_logger(__name__, "info")

module_path = "personal/" # app path, needed to place your app in a correct menu directory
# for app directory paths, see https://github.com/ZeroPhone/ZPUI/tree/master/apps
# (do check that the directory you're using, isn't an app)

class App(ZeroApp):
    menu_name = "Example app" # App name as seen in main menu while using the system

    def init_app(self):
        # this is where you put commands that need to run when ZPUI loads
        # if you want to do something long-winded here, consider using BackgroundRunner!
        # feel free to completely remove this function if it's not used
        pass

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

    def on_start(self):
        """This function is called when you click on the app in the main menu"""
        mc = [ # menu contents
          ["Test", self.test],
        ]
        m = Menu(mc, self.i, self.o) #, name=self.menu_name+" menu")
        logger.info("menu is starting yay")
        m.activate()
        logger.info("menu has exited yay")
        # feel free to shorten this code like this:
        #Menu(mc, self.i, self.o, name=self.menu_name+" menu").activate()

    def test(self):
        # executed when you select "Test" in the menu
        # example for how to read files from the app directory
        text = self.get_text()
        Printer(text, self.i, self.o, 5)

    def get_text(self):
        with open(local_path("text.txt"), 'r') as f:
            text = f.read().strip()
        return text


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
        # feel free to do any further sibstitutions here.
        assert isinstance(app.get_text(), str)

if __name__ == "__main__":
    print("Warning: running this app directly will not make it launch. See the README for installation instructions.\n")
    print("Now, running tests:")
    unittest.main()

