### Reported Issue

Group vars provided inside of the inventory file are returned inside
of the group, but those provided inside of a group_vars folder are not.
Run the `inventory.ini` file for an example:

`./backport.py -i tests/data/bug_gv/inventory.ini --list`

```json
{
    "_meta": {
        "hostvars": {
            "host_inside_group": {
                "agroup_var_from_group_vars_file": true, 
                "agroup_var_from_inventory_file": true
            }
        }
    }, 
    "agroup": {
        "hosts": [
            "host_inside_group"
        ], 
        "vars": {
            "agroup_var_from_inventory_file": true
        }
    }, 
    "all": {
        "children": [
            "agroup", 
            "ungrouped"
        ]
    }, 
    "ungrouped": {
        "hosts": [
            "host_inside_group"
        ]
    }
}
```

Both variables are correctly set on the host, but the variable
`agroup_var_from_inventory_file` is also provided on the group,
which is inconsistent.
