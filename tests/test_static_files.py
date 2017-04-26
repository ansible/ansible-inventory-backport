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


TEST_INVENTORY_INI = '''\
# Some comment about blah blah blah...

[webservers]
web1.example.com ansible_ssh_host=w1.example.net
web2.example.com
web3.example.com:1022

[webservers:vars]   # Comment on a section
webvar=blah

[dbservers]
db1.example.com
db2.example.com

[dbservers:vars]
dbvar=ugh

[servers:children]
webservers
dbservers

[servers:vars]
varb=B

[all:vars]
vara=A

[others]
10.11.12.13
10.12.14.16:8022
fe80::1610:9fff:fedd:654b
[fe80::1610:9fff:fedd:b654]:1022
::1
'''


@pytest.fixture(scope='session')
def test_dir(tmpdir_factory):
    return tmpdir_factory.mktemp('inv_files', numbered=False)


@pytest.fixture(scope='session')
def ini_file(test_dir):
    fn = test_dir.join('test_hosts')
    fn.write(TEST_INVENTORY_INI)
    return fn


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

    def test_host_and_group_vars(self, ini_file, command):
        instance = command(['-i', ini_file.dirname, '--list'])
        instance.options.inventory = ini_file.dirname
        output = self.get_output(instance)
        # Test vars set on hosts individually
        assert output['_meta']['hostvars']['web1.example.com']['ansible_ssh_host'] == 'w1.example.net'
        # Test vars set on a group
        assert output['dbservers']['vars']['dbvar'] == 'ugh'

    def test_inventory_import_group_vars_file(self, ini_file, tmpdir_factory, command):
        # Create an extra group_vars file for group webservers
        f = tmpdir_factory.mktemp('inv_files/group_vars', numbered=False).join('webservers')
        f.write('''webservers_only_variable: foobar\n''')

        instance = command(['-i', ini_file.dirname, '--list'])
        instance.options.inventory = ini_file.dirname
        output = self.get_output(instance)

        for host in ['web1.example.com', 'web2.example.com', 'web3.example.com']:
            assert output['_meta']['hostvars'][host]['webservers_only_variable'] == 'foobar'

    def test_inventory_import_host_vars_file(self, ini_file, tmpdir_factory, command):
        # Create an extra group_vars file for group webservers
        f = tmpdir_factory.mktemp('inv_files/host_vars', numbered=False).join('db1.example.com')
        f.write('''database_only: foobar\n''')

        instance = command(['-i', ini_file.dirname, '--list'])
        instance.options.inventory = ini_file.dirname
        output = self.get_output(instance)

        assert output['_meta']['hostvars']['db1.example.com']['database_only'] == 'foobar'

    def test_ansible_facts_not_in_hostvars(self, test_dir, command):
        fn = test_dir.join('test_hosts')
        fn.write('''foo.bar.com\n''')

        instance = command(['-i', fn.dirname, '--list'])
        instance.options.inventory = fn.dirname
        output = self.get_output(instance)

        assert 'ansible_facts' not in output['_meta']['hostvars']['foo.bar.com']
