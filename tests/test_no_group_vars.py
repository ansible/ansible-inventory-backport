import os

# Backported ansible-inventory plugin
from backport import InventoryCLI  # noqa


TEST_DIR = os.path.dirname(__file__)
EXAMPLE_FILE = os.path.join(TEST_DIR, 'data', 'bug_gv', 'inventory.ini')


def test_no_group_vars(command, get_output):
    instance = command(['-i', EXAMPLE_FILE, '--list'])
    instance.options.inventory = EXAMPLE_FILE
    output = get_output(instance)
    assert 'vars' not in output['agroup']
    hvars = output['_meta']['hostvars']['host_inside_group']
    assert 'agroup_var_from_inventory_file' in hvars
    assert 'agroup_var_from_group_vars_file' in hvars
