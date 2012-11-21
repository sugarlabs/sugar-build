import sys
import time

import tree

ACTIVITIES_WITH_OBJECT_CHOOSER = []

def build_activities_list():
    root = tree.get_root()
    shell = root.find_child(name="sugar-session", role_name="application")

    activities = []

    table = shell.find_child(role_name="table")
    cells = table.find_children(role_name="table cell")

    for row in [cells[i:i+5] for i in range(0, len(cells), 5)]:
        activity_name = row[2].text
        activities.append(activity_name)

    activities.sort()

    return activities

def launch_and_stop_activity(activity_name):
    root = tree.get_root()
    shell = root.find_child(name="sugar-session", role_name="application")

    table = shell.find_child(role_name="table")
    cells = table.find_children(role_name="table cell")

    for row in [cells[i:i+5] for i in range(0, len(cells), 5)]:
        name = row[2].name
        icon = row[1]

        if name == activity_name:
            print "Launching %s" % activity_name 

            time.sleep(10)

            icon.click()

            print "Stopping %s" % activity_name 

            if activity_name in ACTIVITIES_WITH_OBJECT_CHOOSER:
                close_button = shell.find_child(name="Close",
                                                role_name="push button")
                close_button.do_action("click")

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
    root = tree.get_root()
    shell = root.find_child(name="sugar-session", role_name="application")

    done_button = shell.find_child(name="Done", role_name="push button")
    done_button.do_action("click")

    gcr_prompter = root.find_child(name="gcr-prompter", role_name="application")
    if gcr_prompter:
        cancel_button = gcr_prompter.find_child(name="Cancel",
                                                role_name="push button")
        cancel_button.do_action("click")

    radio_button = shell.find_child(name="List view", role_name="radio button")
    radio_button.do_action("click")

def main():
    go_to_list_view()

    for activity in build_activities_list():
        launch_and_stop_activity(activity)

main()
