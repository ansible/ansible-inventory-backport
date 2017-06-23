import pytest
import mock

import os
import sys
import json

import argparse


# Add awx/plugins to sys.path so we can use the plugin
TEST_DIR = os.path.dirname(__file__)
path = os.path.abspath(os.path.join(TEST_DIR, '..'))
if path not in sys.path:
    sys.path.insert(0, path)

# Backported ansible-inventory plugin
from backport import InventoryCLI  # noqa


@pytest.fixture()
def command():
    def make_command(args):
        instance = InventoryCLI(args)
        instance.options = argparse.ArgumentParser(description='Process some integers.')
        instance.options.verbosity = 0
        instance.options.vault_password_file = None
        instance.options.ask_vault_pass = False
        instance.options.inventory = __file__
        instance.options.host = None
        instance.options.graph = False
        instance.options.list = True
        instance.options.yaml = False
        return instance
    return make_command


@pytest.fixture
def get_output():
    def ret(instance):
        # Run command and return output
        with mock.patch('backport.display') as mock_display:
            mock_display_method = mock.MagicMock()
            mock_display.display = mock_display_method
            with pytest.raises(SystemExit):
                instance.run()
            mock_display_method.assert_called()
            output = mock_display_method.mock_calls[0][1][0]
            output = json.loads(output)
        return output
    return ret
