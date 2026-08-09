# 10. Disabling Intel Undervolting due to Firmware Voltage Lock

* **Status:** Accepted
* **Date:** 2026-08-09

## Context

To minimize thermal output and prevent thermal throttling under heavy workloads on 8th-Gen Coffee Lake mini PCs (`mik`, `mak`, `muk`), we initially evaluated software-based CPU/GPU undervolting using `intel-undervolt`. 

However, running `intel-undervolt read` confirms that voltage offsets read as `0.00 mV` across all channels. Intel released a mandatory microcode patch to mitigate the **Plundervolt vulnerability (CVE-2019-11157 / INTEL-SA-00289)**, which permanently locked Model-Specific Register `0x150` (the MSR interface for voltage offsets) at the HP BIOS/firmware layer. 

Attempts to force undervolting result in silent hardware rejections or `intel-undervolt.service` startup failures (`Values do not equal`). While bypassing this lock via pre-2020 BIOS downgrades or custom NVRAM setup-variable injection is technically possible, doing so risks bricking motherboard firmware or exposing the nodes to platform instabilities.

## Decision

* Explicitly disable software undervolting across the cluster.
* Deploy a managed configuration template (`templates/intel-undervolt.conf.j2`) with `enable false` and set all offset values to `0`.
* Stop and disable `intel-undervolt.service` within `playbooks/base-setup.yml`.
* Manage thermals through standard active fan profiles, airflow maintenance (retaining internal SATA drive caddys), and native Linux CPU scaling governors (`intel_pstate=active`).

## Consequences

* **Positive:** Prevents failed Ansible plays, avoids systemd unit startup errors, and maintains standard BIOS security/stability fixes.
* **Negative:** CPU thermal dissipation and power consumption remain at stock Intel factory curves, providing no additional thermal headroom under sustained 100% load.
