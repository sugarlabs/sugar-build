import os
import logging
import traceback

os.environ["AT_SPI_CLIENT"] = "yes"

from sugar3.test import uitree


_activities_list = ["Browse",
                    "Chat",
                    "Read",
                    "Log",
                    "Terminal",
                    "Pippy",
                    "Image Viewer",
                    "Jukebox",
                    "TurtleBlocks",
                    "Write"]


def launch_and_stop_activity(activity_name):
    logging.info("Launching %s" % activity_name)

    root = uitree.get_root()
    shell = root.find_child(name="main.py", role_name="application")

    table = shell.find_child(role_name="table")
    cells = table.find_children(role_name="table cell")

    for row in [cells[i:i + 5] for i in range(0, len(cells), 5)]:
        name = row[2].name
        icon = row[1]

        if name == activity_name:
            icon.do_action("activate")

            logging.info("Stopping %s" % activity_name)

            activity = root.find_child(name="sugar-activity",
                                       role_name="application")

            stop_buttons = activity.find_children(name="Stop",
                                                  role_name="push button")
            stop_buttons[-1].do_action("click")

            activity = root.find_child(name="sugar-activity",
                                       role_name="application",
                                       expect_none=True)
            if activity is not None:
                raise RuntimeError


def go_to_list_view():
    root = uitree.get_root()
    shell = root.find_child(name="main.py", role_name="application")

    radio_button = shell.find_child(name="List view", role_name="radio button")
    radio_button.do_action("click")


def main():
    format = "%(created)f %(message)s"
    logging.basicConfig(format=format)
    logging.root.setLevel(logging.DEBUG)

    logging.info("Start test")

    go_to_list_view()

    for activity in _activities_list:
        launch_and_stop_activity(activity)

try:
    main()
except:
    logging.error(traceback.format_exc())
    logging.error("\n%s" % uitree.get_root().dump())
    raise
