# ADR 0017: A Nachtgespenst Development Environment on mik, in its own Branch

* **Status:** Accepted
* **Date:** 2026-11-25
* **Deciders:** Hans Kruse

---

## Context and Problem Statement

The Nachtgespenst macro pad (M5Stack Core2 and CoreS3 firmware, Java tools, a HID-BPF loader) is built, flashed and
tested from a Linux machine. The laptop `kos` does it today; `mik` should be able to do it as well, with the same
packages, udev rules and HID-BPF loader. [ADR 0005](./0005-separate-scope-for-base-os-and-workload-setup.md) keeps `main`
to the host baseline and [ADR 0014](./0014-git-branching-strategy.md) puts everything else in long-lived branches.

## Decision Outcome

A branch `nachtgespenst`, rebased onto `main` like the `env_*` branches, holds:

* `playbooks/nachtgespenst-setup.yml` and `-teardown.yml`, registered in `setup.yml` and `teardown.yml`;
* the inventory group `nachtgespenst` with the single host `mik`, so `mak` and `muk` are never touched by these
  playbooks; on this branch `mak` and `muk` are also commented out of `cluster_nodes`, because only `mik` is powered on;
* the udev rules for the boards (`files/70-…`, `71-…`, `99-nachtgespenst-esp32-serial.rules`) and the unit of the
  udev-started HID-BPF loader (`files/nachtgespenst-hid-bpf@.service`), copied from the `kos` repository, which is the
  reference for them (its ADR 0016).

Setup installs the packages of the group variable `nachtgespenst_packages` (PlatformIO, esptool, JDK 27 from
`jdk-openjdk`, Node, the BPF tools, `claude-code` with its sandbox tools) and JBang, and records what it installed
itself in `/etc/ansible/facts.d/mikmakmuk_nachtgespenst.fact`, so teardown removes only that. `trufflehog` (the
pre-push hook of the repositories) is not in the repositories: setup installs the release binary of the pinned
`trufflehog_version` with the checksum of the release into `/opt/trufflehog`, unless the AUR package `trufflehog-bin`
is installed. AUR packages (`zoom`) cannot be installed by the pacman module: setup only reports those that are
missing and teardown never removes them. `zoom` is installed on `mik` already and stays.

## Consequences

* `main` stays a pure baseline; the environment can be dropped by not using the branch.
* The loader jar is built in the nachtgespenst repository; until it is installed with
  `-e hid_bpf_loader_jar=/path/to/loader.jar` the unit does nothing.
* The rules and the unit exist in two repositories (`kos` and here); a change has to be made in both.
