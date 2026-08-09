#!/usr/bin/env bash

set -euo pipefail

# Create ADR directory
mkdir -p adr

# -----------------------------------------------------------------------------
# ADR 0001: Record Architecture Decisions
# -----------------------------------------------------------------------------
cat <<'EOF' > adr/0001-record-architecture-decisions.md
# 1. Record Architecture Decisions

* **Status:** Accepted
* **Date:** 2026-08-09

## Context

We need to keep track of important architectural decisions made during the setup and evolution of the Mik Mak Muk cluster to provide context, record tradeoffs, and keep documentation organized.

## Decision

We will use Architecture Decision Records (ADRs) as framed by Michael Nygard. ADRs will be stored in the `adr/` directory of this repository as Markdown files.

## Consequences

* Future structural changes and tradeoffs will be documented in a predictable, reproducible format.
* The main `README.md` can remain focused on installation and operational commands rather than dense design rationales.
EOF

# -----------------------------------------------------------------------------
# ADR 0002: Storage Layout and NVMe-Only Boot Drive Strategy
# -----------------------------------------------------------------------------
cat <<'EOF' > adr/0002-storage-layout-and-nvme-only-boot.md
# 2. Storage Layout and NVMe-Only Boot Drive Strategy

* **Status:** Accepted
* **Date:** 2026-08-09

## Context

Each node in the cluster contains an NVMe SSD (1-2 TB) alongside a secondary SATA drive caddy fitted with a legacy 120 GB SATA SSD. Originally, the intent was to offload OS boot logic to the SATA SSDs and reserve high-speed NVMe storage exclusively for workloads. However, the SATA drives fail to boot cleanly, and ribbon cable reliability across the mini-PC chassis is uncertain.

Additionally, removing the SATA caddy to access secondary NVMe slots introduces cooling complications on the HP EliteDesk 800 Mini G4, as the primary CPU cooling fan mounts directly to the SATA caddy assembly.

## Decision

* Operate all cluster nodes exclusively on NVMe SSD storage for both the OS base and workload paths.
* Keep the SATA drive caddys installed in all nodes to preserve internal airflow dynamics and maintain stock CPU fan mounting points.

## Consequences

* **Positive:** Ensures high-speed boot times, maximum storage reliability, and stock thermal dissipation across all nodes.
* **Negative:** Consumes primary NVMe space for OS runtime partitions and leaves secondary SATA drives unused.
EOF

# -----------------------------------------------------------------------------
# ADR 0003: Physical Desk-Sleeve Mounting Infrastructure
# -----------------------------------------------------------------------------
cat <<'EOF' > adr/0003-physical-desk-sleeve-mounting.md
# 3. Physical Desk-Sleeve Mounting Infrastructure

* **Status:** Accepted
* **Date:** 2026-08-09

## Context

Deploying a traditional 19-inch server rack or custom mini-rack in a home office space incurs unnecessary monetary and spatial overhead for mini-PCs.

## Decision

Mount nodes under a custom monitor desk shelf using official HP under-desk mounting sleeves.

## Consequences

* **Positive:** Minimizes spatial footprint, maintains clean cable routing beneath the monitor shelf, and allows individual nodes to be easily unmounted for standalone desktop usage.
* **Negative:** Limits total cluster expansion to the fixed width beneath the shelf (maximum 4 units).
EOF

# -----------------------------------------------------------------------------
# ADR 0004: Ansible for Declarative Agentless Automation
# -----------------------------------------------------------------------------
cat <<'EOF' > adr/0004-ansible-for-declarative-agentless-automation.md
# 4. Ansible for Declarative Agentless Automation

* **Status:** Accepted
* **Date:** 2026-08-09

## Context

Managing multiple Linux nodes using manual imperative shell scripts leads to drift, non-reproducible host states, and complex recovery paths.

## Decision

Adopt Ansible as the sole configuration management framework for cluster setup, OS tuning, and node teardown.

## Consequences

* **Positive:** Provides agentless management over standard SSH, strict task idempotency (`changed=0` on clean runs), and simple YAML-based task definitions.
* **Negative:** Requires managing OpenSSH authentication mechanics and Python dependency environments on the control laptop.
EOF

# -----------------------------------------------------------------------------
# ADR 0005: Separate Scope for Base OS and Workload Setup
# -----------------------------------------------------------------------------
cat <<'EOF' > adr/0005-separate-scope-for-base-os-and-workload-setup.md
# 5. Separate Scope for Base OS and Workload Setup

* **Status:** Accepted
* **Date:** 2026-08-09

## Context

Mixing base kernel tuning (driver installs, power parameters, CPU mitigations) with orchestration layer setup (Kubernetes, Docker, Incus) creates bloated playbooks that break when changing orchestrators.

## Decision

Decouple hardware platform tuning from workload orchestrators. This repository strictly manages OS and hardware baseline configurations. Downstream container networking (e.g., `overlay`, `br_netfilter`, sysctl IP forwarding) belongs in dedicated downstream repositories or branches.

## Consequences

* **Positive:** The base OS automation remains agnostic to future orchestrator choices (Kubernetes, Incus, systemd-nspawn, Docker).
* **Negative:** Requires running separate playbooks sequentially when bootstrapping new nodes from scratch.
EOF

# -----------------------------------------------------------------------------
# ADR 0006: Standalone Reboot Operations
# -----------------------------------------------------------------------------
cat <<'EOF' > adr/0006-standalone-reboot-operations.md
# 6. Standalone Reboot Operations

* **Status:** Accepted
* **Date:** 2026-08-09

## Context

Modifying kernel command-line parameters (`/etc/cmdline.d/`) and regenerating initramfs (`mkinitcpio -P`) requires a reboot to take effect. Automatically rebooting nodes inside the baseline setup playbook can cause unexpected service disruptions during routine playbook executions.

## Decision

Remove automatic reboot tasks from `base-setup.yml` and provide a dedicated, isolated playbook (`playbooks/reboot.yml`) with `--limit` support.

## Consequences

* **Positive:** Prevents unexpected node restarts during routine configuration runs; enables single-node rolling reboots (`serial: 1`) during active maintenance windows.
* **Negative:** Administrative action is required to manual invoke `reboot.yml` after changing kernel options.
EOF

# -----------------------------------------------------------------------------
# ADR 0007: CPU Undervolting Strategy and Microcode Lock Handling
# -----------------------------------------------------------------------------
cat <<'EOF' > adr/0007-cpu-undervolting-strategy.md
# 7. CPU Undervolting Strategy and Microcode Lock Handling

* **Status:** Accepted
* **Date:** 2026-08-09

## Context

Mini-PC chassis (such as HP ProDesk 400/600/800 G4) experience thermal throttling under sustained heavy CPU workloads. While `intel-undervolt` can reduce power consumption and thermal output, Intel Plundervolt microcode updates locked Model Specific Registers (MSR `0x150`) across many 8th-Gen Coffee Lake BIOS releases.

## Decision

* Maintain a Jinja2 template (`templates/intel-undervolt.conf.j2`) for undervolt configuration management.
* Explicitly disable `intel-undervolt.service` (`enable false` in config, service `state: stopped`, `enabled: false`) across nodes where BIOS/microcode mitigations prevent MSR writes.

## Consequences

* **Positive:** Prevents `intel-undervolt.service` boot/systemd unit failures (`Values do not equal` / exit status 1) on nodes with locked voltage registers.
* **Negative:** Nodes with locked microcode run at factory voltage tables and rely purely on passive/active fan cooling.
EOF

echo "ADRs successfully generated in adr/"
