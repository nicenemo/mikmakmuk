# 10. Removing Intel Undervolting and Thermald from Project Configuration

* **Status:** Accepted
* **Date:** 2026-08-09

## Context

To lower temperatures and prevent thermal throttling under heavy workloads on 8th-Gen Coffee Lake mini-PCs (`mik`, `mak`, `muk`), we evaluated software-based CPU/GPU undervolting via `intel-undervolt` as well as user-space thermal throttling daemons (`thermald`).

However, HP BIOS releases for EliteDesk and ProDesk G4 models permanently locked Model-Specific Register `0x150` (voltage offsets) to mitigate the **Plundervolt vulnerability (CVE-2019-11157)**. Software undervolting attempts fail or result in unapplied `0.00 mV` offsets. Furthermore, running `thermald` interferes with the active Linux kernel scaling governor (`intel_pstate=active`), causing overhead without providing thermal relief due to locked power tables.

## Decision

* Completely remove `intel-undervolt` and `thermald` packages, service units, and configuration files from the project codebase and Ansible playbooks.
* Manage thermals strictly through physical airflow maintenance (retaining SATA drive caddys for proper fan positioning), native Linux CPU performance scaling (`intel_pstate=active`), and standard BIOS fan curves.

## Consequences

* **Positive:** Eliminates dead code, prevents systemd service failures, and keeps the Ansible repository completely lean and aligned with actual target hardware capabilities.
* **Negative:** CPU thermal curves remain at HP/Intel factory limits without extra software-defined thermal control.
