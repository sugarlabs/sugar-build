from dogtail import tree
from dogtail import predicate

shell = tree.root.child(name="sugar-session", roleName="application")

# Complete the intro screen
done_button = shell.child(name="Done", roleName="push button")
done_button.click()

# Switch to the home list view
radio_button = shell.child(name="List view", roleName="radio button")
radio_button.click()

# Start and stop all the activities in the table
table = shell.child(name="", roleName="table")
cells = table.findChildren(predicate.GenericPredicate(roleName="table cell"))

for row in [cells[i:i+5] for i in range(0, len(cells), 5)]:
    print "Launching %s" % row[2].text

    row[1].click()

    activity = tree.root.child(name="sugar-activity", roleName="application")
    stop_button = activity.child(name="Stop", roleName="push button")
    stop_button.click()
