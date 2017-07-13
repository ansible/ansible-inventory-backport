import pytest
import mock
import json

# python
import os
import sys
import argparse
import cStringIO

# Add awx/plugins to sys.path so we can use the plugin
TEST_DIR = os.path.dirname(__file__)
path = os.path.abspath(os.path.join(TEST_DIR, '..'))
if path not in sys.path:
    sys.path.insert(0, path)

# Backported ansible-inventory plugin
from backport import InventoryCLI  # noqa

# Primary version of ansible-inventory
try:
    from ansible.cli.inventory import InventoryCLI as ansible_CLI
except ImportError:
    ansible_CLI = None


TEST_DIR = os.path.dirname(__file__)
EXAMPLE_FILE = os.path.join(TEST_DIR, 'data', 'everything', 'inventory.ini')


@pytest.mark.skipif(ansible_CLI is None, reason="Only testing post-2.4 behavior")
def test_full_group_vars():
    run = ansible_CLI(['ansible-inventory', '-i', EXAMPLE_FILE, '--local', '--list'])
    run.parse()
    stdout_ = sys.stdout
    stream = cStringIO.StringIO()
    try:
        sys.stdout = stream
        run.run()
    except SystemExit:
        pass
    finally:
        sys.stdout = stdout_
        output = stream.getvalue()
    inv_dict = json.loads(output)
    assert 'group_2' in inv_dict
    assert '_meta' in inv_dict
    assert 'hostvars' in inv_dict['_meta']
    assert set(['host_1', 'host_2', 'host_ungrouped']) == set(inv_dict['_meta']['hostvars'].keys())
    assert {} == inv_dict['_meta']['hostvars']['host_2'] == inv_dict['_meta']['hostvars']['host_ungrouped']
    assert {
        "hostvar_inventory": "defined_in_inventory_file",
        "hostvar_file": "defined_in_host_vars"
    } == inv_dict['_meta']['hostvars']['host_1']
    assert {
        "groupvar_file": "defined_in_group_vars", 
        "groupvar_inventory": "defined_in_inventory_file"
    } == inv_dict['group_1']['vars']

