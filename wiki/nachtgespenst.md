# Nachtgespenst environment on mik (branch `nachtgespenst`)

[ADR 0017](../adr/0017-nachtgespenst-branch-for-mik.md). Only `mik` is in the group `nachtgespenst`.

## Install

```bash
git switch nachtgespenst
./setup.yml --limit mik                  # the whole baseline plus the Nachtgespenst environment
ansible-playbook playbooks/nachtgespenst-setup.yml
```

With the loader jar of the nachtgespenst repository (`docs/plans/hid-ebpf-leds.md` there):

```bash
ansible-playbook playbooks/nachtgespenst-setup.yml -e hid_bpf_loader_jar=/path/to/loader.jar
```

## Check

```bash
systemctl list-units 'nachtgespenst-hid-bpf@*'
sudo bpftool prog list | grep -i hid
ls /sys/fs/bpf/nachtgespenst
```

## Remove

```bash
ansible-playbook playbooks/nachtgespenst-teardown.yml
```

Packages that were on `mik` before setup (and `zoom`) stay.
