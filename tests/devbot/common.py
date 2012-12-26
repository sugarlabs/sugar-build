import os
import unittest
import tempfile

from devbot import config


class DevbotTestCase(unittest.TestCase):
    def setUp(self):
        self.setup_config()

    def setup_config(self, extra_args):
        temp_dir = tempfile.gettempdir()

        args = {"logs_dir": os.path.join(temp_dir, "logs"),
                "source_dir": os.path.join(temp_dir, "source"),
                "build_dir": os.path.join(temp_dir, "build"),
                "install_dir": os.path.join(temp_dir, "install"),
                "state_dir": os.path.join(temp_dir, "state")}

        args.update(extra_args)

        config.setup(**args)
