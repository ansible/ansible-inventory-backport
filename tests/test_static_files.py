import pytest

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


class TestLoadFile:

    def test_host_and_group_vars(self, ini_file, command, get_output):
        instance = command(['-i', ini_file.dirname, '--list'])
        instance.options.inventory = ini_file.dirname
        output = get_output(instance)
        # Test vars set on hosts individually
        assert output['_meta']['hostvars']['web1.example.com']['ansible_ssh_host'] == 'w1.example.net'

    def test_inventory_import_group_vars_file(self, ini_file, tmpdir_factory, command, get_output):
        # Create an extra group_vars file for group webservers
        f = tmpdir_factory.mktemp('inv_files/group_vars', numbered=False).join('webservers')
        f.write('''webservers_only_variable: foobar\n''')

        instance = command(['-i', ini_file.dirname, '--list'])
        instance.options.inventory = ini_file.dirname
        output = get_output(instance)

        for host in ['web1.example.com', 'web2.example.com', 'web3.example.com']:
            assert output['_meta']['hostvars'][host]['webservers_only_variable'] == 'foobar'

    def test_inventory_import_host_vars_file(self, ini_file, tmpdir_factory, command, get_output):
        # Create an extra group_vars file for group webservers
        f = tmpdir_factory.mktemp('inv_files/host_vars', numbered=False).join('db1.example.com')
        f.write('''database_only: foobar\n''')

        instance = command(['-i', ini_file.dirname, '--list'])
        instance.options.inventory = ini_file.dirname
        output = get_output(instance)

        assert output['_meta']['hostvars']['db1.example.com']['database_only'] == 'foobar'

    def test_ansible_facts_not_in_hostvars(self, test_dir, command, get_output):
        fn = test_dir.join('test_hosts')
        fn.write('''foo.bar.com\n''')

        instance = command(['-i', fn.dirname, '--list'])
        instance.options.inventory = fn.dirname
        output = get_output(instance)

        assert 'ansible_facts' not in output['_meta']['hostvars']['foo.bar.com']
