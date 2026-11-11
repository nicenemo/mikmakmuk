# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

Agentless Ansible automation for **The Mik Mak Muk Cluster**: three HP Mini G4 nodes (`mik`, `mak`, `muk`) running
CachyOS. Scope on `main` is strictly the **host OS / hardware baseline** (kernel cmdline, iGPU drivers, NVMe/fstab/TRIM,
USB-C cluster network, benchmarks). Container/orchestrator setup (Docker, Incus, K8s, nspawn, …) does **not** belong on
`main` — it lives in long-lived `env_*` branches rebased onto `main` (ADR 0005, ADR 0014). Design rationale for most
choices is in `adr/`; read the relevant ADR before changing a deliberate decision (e.g. `mitigations=off`, no
undervolting/thermald, unencrypted ansible SSH key).

Note: the directory tree in `AGENTS.md` is outdated — static files live in top-level `files/` and Jinja reports in
`templates/`, not under `playbooks/`.

## Running playbooks

All playbooks are executable (`#!/usr/bin/env ansible-playbook` shebang) and run from the repo root, where
`ansible.cfg` sets `inventory = inventory.yml`, `become = True`, and the key `~/.ssh/id_ed25519_ansible`.

```bash
./controller-setup.yml          # localhost: create ansible SSH keypair (no -K)
./ansible-user-setup.yml -K     # as bootstrap_user (kruse): create myansibleuser w/ NOPASSWD sudo (needs -K)
./setup.yml                     # full baseline via myansibleuser (no -K)
./teardown.yml                  # revert baseline (no -K)
./ansible-user-teardown.yml -K  # remove myansibleuser (needs -K)
./controller-teardown.yml       # delete local keypair (no -K)
./reboot.yml                    # rolling reboot, serial: 1
./benchmark.yml                 # all benchmarks -> JSON in /tmp/mikmakmuk-benchmarks + Markdown report

ansible-playbook playbooks/kernel-setup.yml --limit muk   # single sub-playbook, single node
ansible-playbook setup.yml --check --diff                 # dry run
ansible-playbook playbooks/benchmark-cpu.yml --limit mak  # single benchmark, single node
```

The report/index playbooks are `hosts: localhost` plays, so `--limit` skips them; run them separately afterwards (or
add `localhost` to the limit).

`-K` is only for plays that connect as `bootstrap_user`; everything else uses `ansible_management_user`
(`myansibleuser`) with passwordless sudo. Repeated wrong sudo passwords trigger `pam_faillock` lockouts
(`sudo faillock --user kruse --reset`).

## Linting

```bash
ansible-lint
yamllint .                       # config: .yamllint (120 cols, ansible-lint compatible)
markdownlint-cli2 "**/*.md"     # config: .markdownlint-cli2.yaml (ignores playbooks/, asterisk lists, 120 cols)
editorconfig-checker
prettier --check .
```

There are no tests and no CI; verification is running against the nodes (teardown → setup cycle is the idempotency
test). The GitHub Pages site (`index.html`) and its benchmark publishing playbook live on `main` only.

## Architecture

* **Orchestrators**: `setup.yml` and `teardown.yml` are just `import_playbook` lists of `playbooks/*-setup.yml` /
  `*-teardown.yml`. Every `*-setup.yml` should have a matching `*-teardown.yml` that cleanly reverts it, and
  `teardown.yml` runs them in reverse order of `setup.yml`. When adding a new setup playbook, add its teardown and
  register both in the orchestrators.
* **No benchmarks in setup**: nothing imported by `setup.yml` may benchmark or stress the nodes. All measurement lives
  in `playbooks/benchmark-*.yml`, orchestrated by root `benchmark.yml`.
* **Benchmark pipeline**: each `benchmark-*.yml` compiles a dict of plain numbers/strings and imports
  `playbooks/tasks/save-benchmark-result.yml`, which writes `<benchmark_results_dir>/<benchmark>/<host>.json` on the
  controller (`delegate_to: localhost`, outside the repo; override with `MIKMAKMUK_BENCHMARK_DIR`).
  `benchmark-report.yml` loads those files via `tasks/load-benchmark-results.yml` and renders
  `templates/benchmark_report.md.j2` into a Markdown report. Which metrics appear, with
  labels/units/precision, is defined once in `benchmark_report_sections` in `playbooks/vars/benchmark.yml`; adding a
  metric means emitting it in the benchmark's result dict and listing it there. Benchmark-only packages are listed in
  `benchmark_tool_packages` (installed by the benchmarks, removed by `base-teardown.yml`).
* **Native modules first**: use a module whenever one exists (`systemd_service`, `nmcli state: up`,
  `ansible.posix.sysctl`, `setup` with a `gather_subset` refresh for kernel/network/mount/clock facts, `slurp` for
  sysfs). `ansible.builtin.command` is only for running the measurement/system tools themselves (benchmarks, `lscpu`,
  `smartctl`, `mkinitcpio`, …) with argv-style arguments; never `shell` or `script` (the nodes' login shell is fish).
  Loops, timing, background services and cleanup are Ansible constructs (`until`, `async`/`async_status`, runtime units
  from `templates/` in `/run/systemd/system`, `block`/`always`), not shell scripts. Don't paper over errors with
  `failed_when: false`/`ignore_errors`; guard with `stat`/facts instead.
* **Tool output parsing**: prefer machine-readable output (`sensors -j`, `lscpu --json`, `smartctl --json`, fio/iperf3
  `--json`, clpeak `--output`, stress-ng `--yaml` + `slurp`) parsed in Jinja.
* **Lint constraints**: `ansible-lint` flags every `run_once`, so cross-host aggregation happens in `hosts: localhost`
  plays or on the controller; Jinja regex strings inside folded `>-` scalars take single backslashes (`\s`); only
  double-quoted YAML needs `\\s`.
* **Path resolution**: playbooks under `playbooks/` see `playbook_dir` = `playbooks/` even when imported, so repo-root
  `files/` and `templates/` are reached via `project_root` (`{{ playbook_dir | dirname }}`, defined in
  `vars/benchmark.yml`; older playbooks use an equivalent conditional expression).
* **Kernel cmdline**: `files/homelab-tuning.conf` is the single source of kernel parameters. `kernel-setup.yml` appends
  its tokens to `KERNEL_CMDLINE[default]` in `/etc/default/limine`, runs `limine-entry-tool`, then pins
  `default_entry` in `/boot/limine.conf`; `kernel-teardown.yml` strips the same tokens. The bootloader is Limine (not
  GRUB/systemd-boot).
* **Inventory** (`inventory.yml`): group `cluster_nodes`; per-host vars like `cluster_ip` (192.168.107.x on the USB-C
  cluster VLAN, NetworkManager connection `cluster-vlan107`), `btrfs_mount_opts`, `node_packages`, `cpu_type`;
  shared `common_packages`. Management network is 192.168.105.x.
* **Conventions**: Arch/CachyOS only (`community.general.pacman`, `pacman` commands); FQCN module names; tasks grouped
  under numbered `# ----` section comments; `changed_when`/`creates` on command/shell tasks to keep idempotency.
