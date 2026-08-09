# ADR 0011: Selection of CachyOS as the Host Operating System

* **Status:** Accepted
* **Date:** 2026-08-09
* **Deciders:** Cluster Operator
* **Technical Story:** Choosing a performant, lightweight, and modern Linux distribution for an 8th-Gen Intel (Coffee Lake) Mini-PC cluster (`mik`, `mak`, `muk`).

---

## Context and Problem Statement

The "Mik Mak Muk" cluster consists of legacy 8th-Gen Intel hardware (HP EliteDesk/ProDesk Mini G4) featuring 6-core Intel i5-8500 / i5-8500T CPUs. These desktop-class CPUs lack enterprise features like ECC memory or massive core counts, making resource efficiency, low idle latency, and optimal CPU scheduling critical. 

Standard enterprise server distributions (e.g., Debian, Ubuntu Server, Rocky Linux) run older kernels with conservative configurations, requiring manual tuning to backport modern CPU schedulers, optimized hardware video acceleration drivers, and kernel optimizations for NVMe/I/O. We needed an OS that delivers peak hardware performance out-of-the-box while remaining lightweight and declarative to automate via Ansible.

---

## Decision Drivers

* **Performance & Instruction Set Optimization:** Full leverage of x86-64-v3 instructions (AVX2, FMA3, BMI2) supported by Coffee Lake CPUs.
* **Advanced CPU Schedulers:** Native access to performance-oriented schedulers (such as BORE/EEVDF) for micro-workloads, containers, and low-latency task processing.
* **Up-to-Date Kernel & Driver Stack:** Direct, rolling access to the latest Linux kernels and Intel i915 / VA-API graphics drivers without manual backports.
* **Minimal Base Overhead:** A lean baseline with minimal background daemons running prior to orchestration workloads.
* **Automation Friendliness:** Arch-based ecosystem compatibility with `pacman` and declarative configuration via Ansible.
* **Default BTRFS** Easy snapshotting and volumes with BTRFS which can be used both in Docker as wel as Incus. BTRFS does not have the overhead of ZFS.

---

## Considered Options

1. CachyOS (Arch-based performance-focused distro)
2. Debian Stable
3. Talos Linux / Incus OS/ Proxmox

---

## Decision Outcome

Chosen Option: **Option 1 — CachyOS**. This is a homelab, not a business!

CachyOS provides pre-compiled `x86-64-v3` optimized package repositories and custom Linux kernels equipped with advanced CPU schedulers. This maximizes the IPC (instructions per cycle) and responsive power management of the Intel i5-8500/T processors.

### Positive Consequences

* **Hardware Optimization (`x86-64-v3`):** CachyOS automatically targets the `x86-64-v3` microarchitecture supported by Intel 8th-gen CPUs, yielding performance gains in computational and containerized workloads.
* **Modern Kernel Parameters out-of-the-box:** Seamless integration with modern kernel parameters `intel_pstate=active`, GuC/HuC firmware loading for Intel UHD 630 iGPU offloading.
* **Rolling Release Model:** Eliminates major distribution upgrade downtime; packages are continuously updated via `pacman -Syu` in automated playbook.
* **Agile Automation:** Minimal default setup fits cleanly into the single-purpose Ansible playbook strategy defined in [ADR 0005](./0005-separate-scope-for-base-os-and-workload-setup.md).

### Negative Consequences & Mitigation

* **Rolling Release Risk:** Bleeding-edge updates can occasionally introduce kernel or driver regressions.
  * *Mitigation:* System boots and base configurations are fully declarative and managed via Ansible. If a node fails, it can be reprovisioned via Ventoy and Ansible in minutes.
* **Higher Maintenance Frequency:** Requires periodic updates to Arch and CachyOS keyrings before package upgrades.
  * *Mitigation:* Handled seamlessly inside the `setup.yml` base playbook.

---

## Pros and Cons of the Options

### Debian Stable

* **Good:** Extremely stable, predictable release cycles, widespread documentation.
* **Bad:** Conservative, Ships older kernels; missing default `x86-64-v3` compiled binaries; possible outdated i915 GuC/HuC firmware support out of the box; requires extra repository management overhead.

### Talos Linux / IncusOS /Proxmox

* **Good:** Purpose-built for Kubernetes, Incus, vm loads.
* **Bad:** Limits host-level hardware customization (such as disabling CPU mitigations, tuning custom sysctl/kernel parameters, or granular iGPU VA-API driver provisioning) before orchestration.

---

## Links

* [ADR 0005: Separate Scope for Base OS and Workload Setup](./0005-separate-scope-for-base-os-and-workload-setup.md)
* [ADR 0008: Disabling CPU Security Mitigations](./0008-disabling-cpu-security-mitigations.md)
