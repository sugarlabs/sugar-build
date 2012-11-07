import pyatspi

def get_root():
    return Node(pyatspi.Registry.getDesktop(0))

class Node:
    def __init__(self, accessible):
        self._accessible = accessible

    def _predicate(self, accessible, name, role_name): 
        if name is not None and name != accessible.name:
            return False

        if role_name is not None and role_name != accessible.getRoleName():
            return False

        return True

    def find_child(self, name=None, role_name=None):
        def predicate(accessible):
            return self._predicate(accessible, name, role_name)

        accessible = pyatspi.findDescendant(self._accessible, predicate)

        return Node(accessible)

    def find_children(self, name=None, role_name=None):
        def predicate(accessible):
            return self._predicate(accessible, name, role_name)

        all_accessibles = pyatspi.findAllDescendants(self._accessible, predicate)

        return [Node(accessible) for accessible in all_accessibles]

    def _dump_accessible(self, accessible, depth):
        print "" * depth + str(accessible)

    def _crawl_accessible(self, accessible, depth):
        self._dump_accessible(accessible, depth)

        for child in self.find_children():
            self._crawl_accessible(child, depth + 1)

    def dump(self):
        self._crawl_accessible(self._accessible, 0)

    def do_action(self, name):
        action = self._accessible.queryAction()
        for i in range(action.nActions):
            if action.getName(i) == name:
                action.doAction(i)

    def click(self, button=1):
        component = self._accessible.queryComponent()
        x, y = component.getPosition(pyatspi.DESKTOP_COORDS)
        pyatspi.Registry.generateMouseEvent(x, y, "b%sc" % button)

    @property
    def name(self):
        return self._accessible.name

    @property
    def text(self):
        return self._accessible.queryText().getText(0, -1)
