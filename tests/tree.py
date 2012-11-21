import time

import pyatspi

def get_root():
    return Node(pyatspi.Registry.getDesktop(0))

def retry_find(func):
    def wrapped(*args, **kwargs):
        result = None
        n_retries = 1

        while n_retries <= 10:
            print "Try %d, name=%s role_name=%s" % \
                  (n_retries,
                   kwargs.get("name", None),
                   kwargs.get("role_name", None))

            result = func(*args, **kwargs)
            expect_none = kwargs.get("expect_none", False)
            if (not expect_none and result) or \
               (expect_none and not result):
                return result

            time.sleep(5)
            n_retries = n_retries + 1

        get_root().dump()

        return result

    return wrapped

class Node:
    def __init__(self, accessible):
        self._accessible = accessible

    def _predicate(self, accessible, name, role_name): 
        if name is not None and name != accessible.name:
            return False

        if role_name is not None and role_name != accessible.getRoleName():
            return False

        return True

    @retry_find
    def find_child(self, name=None, role_name=None, expect_none=False):
        def predicate(accessible):
            return self._predicate(accessible, name, role_name)

        accessible = pyatspi.findDescendant(self._accessible, predicate)
        if accessible is None:
            return None

        return Node(accessible)

    @retry_find
    def find_children(self, name=None, role_name=None):
        def predicate(accessible):
            return self._predicate(accessible, name, role_name)

        all_accessibles = pyatspi.findAllDescendants(self._accessible, predicate)
        if not all_accessibles:
            return []

        return [Node(accessible) for accessible in all_accessibles]

    def _dump_accessible(self, node, depth):
        print "  " * depth + str(node._accessible)

    def _crawl_accessible(self, node, depth):
        self._dump_accessible(node, depth)

        for child in node._accessible:
            self._crawl_accessible(Node(child), depth + 1)

    def dump(self):
        self._crawl_accessible(self, 0)

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
