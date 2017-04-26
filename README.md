# ansible-inventory-backport

This repository hosts the script `backport.py` as a stand-alone implementation
of the `ansible-inventory` CLI command that works for Ansible 2.2 and 2.3
versions.

## Using

```
./backport.py -i your_inventory --list
```

## Testing

Inside of current directory:

```
py.test
flake8
```

Running against multiple Ansible versions is a work in progress.

## History

The original branch-point was the `ansible-inventory` pull request in
the Ansible repository.

https://github.com/bcoca/ansible/blob/a689d6a54bcaff2e686c95f0933a9b3519e9c209/lib/ansible/cli/inventory.py

The first version of this backport was developed by Chris Church.

https://gist.github.com/cchurch/3b6027d3816c0ea3efe42b55ba924c09

This repository will provide the upstream for future changes, as well
as tests.

### Changelog

Changes to the ansible-inventory development will need to be applied to this
script if possible/applicable, but its development may also diverge.

 - add `ansible_facts` to INTERNAL_VARS
 - flake8 compliance
