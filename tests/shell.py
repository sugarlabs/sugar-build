from operator import attrgetter

from dogtail import tree
from dogtail import predicate

ACTIVITIES_WITH_OBJECT_CHOOSER = ["Read", "Image Viewer", "Jukebox"]
ACTIVITIES_MULTIPLE_STOP = ["Pippy"]

class ActivityLauncher:
    def __init__(self, name=None, icon=None):
        self.name = name
        self.icon = icon

def get_activity_launchers(shell):
    # Make a list of activities by iterating the table
    activity_launchers = []

    table = shell.child(name="", roleName="table")
    pred = predicate.GenericPredicate(roleName="table cell")
    cells = table.findChildren(pred)

    for row in [cells[i:i+5] for i in range(0, len(cells), 5)]:
        launcher = ActivityLauncher(name=row[2].text, icon=row[1])
        activity_launchers.append(launcher)

    activity_launchers.sort(key=attrgetter("name"))

    return activity_launchers

shell = tree.root.child(name="sugar-session", roleName="application")

# Complete the intro screen
done_button = shell.child(name="Done", roleName="push button")
done_button.click()

# Switch to the home list view
radio_button = shell.child(name="List view", roleName="radio button")
radio_button.click()

# Launch and close all the activities
for activity_launcher in get_activity_launchers(shell):
    print "Launching %s" % activity_launcher.name 

    activity_launcher.icon.click()

    if activity_launcher.name in ACTIVITIES_WITH_OBJECT_CHOOSER:
        close_button = shell.child(name="Close", roleName="push button")
        close_button.click()

    activity = tree.root.child(name="sugar-activity", roleName="application")

    if activity_launcher.name in ACTIVITIES_MULTIPLE_STOP:
        toolbar = activity.child(roleName="tool bar")
        pred = predicate.GenericPredicate(name="Stop", roleName="push button")
        stop_buttons = toolbar.findChildren(pred)
        stop_buttons[-1].click()
    else:
        stop_button = activity.child(name="Stop", roleName="push button")
        stop_button.click()
