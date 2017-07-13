import pytest
import mock
import json

# python
import os
import sys
import argparse

# Add awx/plugins to sys.path so we can use the plugin
TEST_DIR = os.path.dirname(__file__)
path = os.path.abspath(os.path.join(TEST_DIR, '..'))
if path not in sys.path:
    sys.path.insert(0, path)

# Backported ansible-inventory plugin
from backport import InventoryCLI  # noqa


EXAMPLE_FILE = os.path.join(TEST_DIR, 'data', 'legacy', 'inventory.ini')


@pytest.fixture()
def command():
    def make_command(args):
        instance = InventoryCLI(args)
        instance.parse()
        return instance
    return make_command


class TestLoadFile:

    def get_output(self, instance):
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

    def test_host_and_group_vars(self, command):
        instance = command(['-i', EXAMPLE_FILE, '--list'])
        instance.options.inventory = EXAMPLE_FILE
        output = self.get_output(instance)
        # Test vars set on hosts individually
        assert output['_meta']['hostvars']['web1.example.com']['ansible_ssh_host'] == 'w1.example.net'
        # Test vars set on a group
        assert output['dbservers']['vars']['dbvar'] == 'ugh'

    def test_inventory_import_group_vars_file(self, command):
        # Test variables defined in group_vars directory

        instance = command(['-i', EXAMPLE_FILE, '--list'])
        instance.options.inventory = EXAMPLE_FILE
        output = self.get_output(instance)

        for host in ['web1.example.com', 'web2.example.com', 'web3.example.com']:
            assert output['_meta']['hostvars'][host]['webservers_only_variable'] == 'foobar'

    def test_inventory_import_host_vars_file(self, command):
        # Test variables defined in host_vars directory

        instance = command(['-i', EXAMPLE_FILE, '--list'])
        instance.options.inventory = EXAMPLE_FILE
        output = self.get_output(instance)

        assert output['_meta']['hostvars']['db1.example.com']['database_only'] == 'foobar'

    def test_ansible_facts_not_in_hostvars(self, command):
        fn = os.path.join(TEST_DIR, 'data', 'single_host', 'single_host')

        instance = command(['-i', fn, '--list'])
        instance.options.inventory = fn
        output = self.get_output(instance)

        assert 'ansible_facts' not in output['_meta']['hostvars']['foo.bar.com']
