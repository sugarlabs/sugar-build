import sys
from time import sleep

from dogtail import tree
from dogtail import predicate
from dogtail import dump

ACTIVITIES_WITH_OBJECT_CHOOSER = ["Read", "Image Viewer", "Jukebox"]
ACTIVITIES_TO_IGNORE = ["Pippy"]

def build_activities_list():
    shell = tree.root.child(name="sugar-session", roleName="application")

    activities = []

    table = shell.child(name="", roleName="table")
    pred = predicate.GenericPredicate(roleName="table cell")
    cells = table.findChildren(pred)

    for row in [cells[i:i+5] for i in range(0, len(cells), 5)]:
        activity_name = row[2].text
        if activity_name not in ACTIVITIES_TO_IGNORE:
            activities.append(activity_name)

    activities.sort()

    return activities

def launch_and_stop_activity(activity_name):
    shell = tree.root.child(name="sugar-session", roleName="application")

    table = shell.child(name="", roleName="table")
    pred = predicate.GenericPredicate(roleName="table cell")
    cells = table.findChildren(pred)

    for row in [cells[i:i+5] for i in range(0, len(cells), 5)]:
        name = row[2].name
        icon = row[1]

        if name == activity_name:
            print "Launching %s" % activity_name 

            icon.click()

            print "Stopping %s" % activity_name 

            if activity_name in ACTIVITIES_WITH_OBJECT_CHOOSER:
                close_button = shell.child(name="Close",
                                           roleName="push button")
                close_button.click()

            activity = tree.root.child(name="sugar-activity",
                                       roleName="application")

            stop_button = activity.child(name="Stop", roleName="push button")
            stop_button.click()

def go_to_list_view():
    shell = tree.root.child(name="sugar-session", roleName="application")

    done_button = shell.child(name="Done", roleName="push button")
    done_button.click()

    sleep(10)

    radio_button = shell.child(name="List view", roleName="radio button")
    radio_button.click()

def main():
    go_to_list_view()

    for activity in build_activities_list():
        sleep(10)
        launch_and_stop_activity(activity)

try:
    main()
except tree.SearchError:
    print "\nDumping the accessible tree\n"
    dump.plain(tree.root)
    sys.exit(1)
