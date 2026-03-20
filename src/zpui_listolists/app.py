from zpui_lib.helpers import setup_logger, local_path_gen, read_or_create_config, save_config_method_gen
from zpui_lib.ui import PrettyPrinter as Printer, Menu, UniversalInput, DialogBox, MenuExitException
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
deleted: []
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
        mc = [
          ["Add lists", self.add_list],
          ["Edit names", self.edit_names],
          ["Rename app", self.rename_app],
        ]
        Menu(mc, self.i, self.o, name=self.menu_name+" settings menu").activate()

    def add_list(self):
        name = UniversalInput(self.i, self.o, message="List name:", name="New list name input").activate()
        if name:
            list_obj = {"name":name, "entries":[]}
            self.config["lists"].append(list_obj)
            self.save_config()

    def rename_app(self):
        current_name = self.menu_name
        name = UniversalInput(self.i, self.o, value=current_name, message="App name:", name="New app name input").activate()
        if name:
            self.menu_name = name
            self.config["app_name"] = name
            self.save_config()

    def edit_names(self):
        def get_contents():
            mc = []
            for index, list in enumerate(self.config["lists"]):
                mc.append([list.get("name", "List name missing!"), lambda x=index: self.edit_name(x)])
            return mc
        Menu([], self.i, self.o, contents_hook=get_contents, name=self.menu_name+" names edit menu").activate()

    def edit_name(self, index):
        current_name = self.config["lists"][index].get("name", "")
        name = UniversalInput(self.i, self.o, value=current_name, message="List name:", name=f"List {index} ({current_name}) name input").activate()
        if name:
            self.config["lists"][index]["name"] = name
            self.save_config()

    def add_entry(self, list_index):
        entry = UniversalInput(self.i, self.o, message="Entry name:", name=f"List {list_index} new entry name input").activate()
        if entry:
            self.config["lists"][list_index]["entries"].append(entry)
            self.save_config()

    def edit_entry(self, list_index, entry_index):
        current_name = self.config["lists"][list_index]["entries"][entry_index]
        entry = UniversalInput(self.i, self.o, value=current_name, message="Entry name:", name=f"List {list_index} entry name edit input").activate()
        if entry:
            self.config["lists"][list_index]["entries"][entry_index] = entry
            self.save_config()
        elif entry == "": # empty string and not None - so the user removed entry contents and pressed Enter, instead of pressing Left
            # removing the entry from the list!
            self.config["lists"][list_index]["entries"].pop(entry_index)
            self.save_config()

    def remove_entry(self, list_index, entry_index):
        db = DialogBox("yn", self.i, self.o, message="Remove entry?", name=self.menu_name+f"entry {list_index} {entry_index} removal DialogBox")
        answer = db.activate()
        if not answer:
            return
        entry = self.config["lists"][list_index]["entries"].pop(entry_index)
        self.config["deleted"].append({"type":"entry", "list_index":list_index, "contents":entry})
        self.save_config()
        raise MenuExitException

    def entry_menu(self, list_index, entry_index):
        mc = [
            ["Rename entry", lambda: self.edit_entry(list_index, entry_index)],
            ["Remove entry", lambda: self.remove_entry(list_index, entry_index)],
        ]
        Menu(mc, self.i, self.o, name=self.menu_name+f" entry {list_index} {entry_index} options menu").activate()

    def list_menu(self, list_index):
        def get_contents():
            mc = []
            list = self.config["lists"][list_index]
            for entry_index, entry in enumerate(list.get("entries", [])):
                mc.append([entry,
                           lambda x=entry_index: self.edit_entry(list_index, x),
                           lambda x=entry_index: self.entry_menu(list_index, x),
                ])
            mc.append(["Add entry", lambda: self.add_entry(list_index)])
            return mc
        Menu([], self.i, self.o, contents_hook=get_contents, name=self.menu_name+f" list {list_index} menu").activate()

    def list_options(self, list_index):
        mc = [
            ["Rename list", lambda: self.remove_list(list_index)],
            ["Remove list", lambda: self.edit_name(list_index)]
        ]
        Menu(mc, self.i, self.o, name=self.menu_name+f" list {list_index} options menu").activate()

    def remove_list(self, list_index):
        db = DialogBox("yn", self.i, self.o, message="Remove list?", name=self.menu_name+f"list {list_index} removal DialogBox")
        answer = db.activate()
        if not answer:
            return
        list = self.config["lists"].pop(list_index)
        self.config["deleted"].append({"type":"list", "contents":list})
        self.save_config()
        raise MenuExitException

    def on_start(self):
        """This function is called when you click on the app in the main menu"""
        def get_contents():
            mc = []
            for index, list in enumerate(self.config["lists"]):
                mc.append([list.get("name", "List name missing!"), \
                lambda x=index: self.list_menu(x), \
                lambda x=index: self.list_options(x),])
            mc.append(["Settings", self.settings_menu])
            return mc
        m = Menu([], self.i, self.o, contents_hook=get_contents, name=self.menu_name+" main menu")
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

