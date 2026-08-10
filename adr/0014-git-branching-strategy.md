# ADR 0014: Git Branching Strategy for Isolation of Service Orchestration Engines

- **Status:** Accepted
- **Date:** 2026-08-10
- **Deciders:** Hans Kruse

---

## Context and Problem Statement

Following the decoupling of base OS hardware tuning from workload orchestrators, the project requires a maintainable strategy to manage distinct runtime environments on top of the CachyOS baseline.

We run multiple container and service orchestration platforms: specifically **host OS package manager services**, **external download services**, **systemd-nspawn**, **Incus**, **Docker**, and **Kubernetes**. Attempting to maintain all runtime playbooks in a single `main` branch creates unnecessary playbook complexity and configuration drift. We need a branching model that isolates each runtime stack while allowing hardware baseline updates applied on `main` to be easily rebased across all downstream environments.

---

## Decision Drivers

- **Scope Decoupling:** Align strictly with [ADR 0005](https://www.google.com/search?q=./0005-separate-scope-for-base-os-and-workload-setup.md) by maintaining a pure host hardware baseline on `main`.
- **Rebase Ergonomics:** Base OS changes (e.g., kernel flags, systemd configs, firewall defaults) must propagate smoothly to downstream stacks via git rebase without merge commits.
- **Workload Isolation:** Prevent overlay networking, custom sysctls, and container engine binaries for one environment (e.g., Kubernetes) from bleeding into another (e.g., Incus or native host services).

---

## Decision Outcome

Chosen Option: **Dedicated downstream orchestration branches rebased against `main**`.

The repository `main` branch is strictly reserved for host OS deployment, x86-64-v3 kernel tuning, and bare-metal baseline automation. Each orchestration and service engine is developed in a long-lived downstream branch using flat branch naming (`env_*`).

**Branch Topology & Stack Mapping**

- **`main`**: Target CachyOS base OS setup, kernel parameters (`mitigations=off`), network drivers, and base security controls.
- **`env_pkg`**: Services and applications installed natively via the CachyOS/Arch host package manager (`pacman`).
- **`env_download`**: Direct binary or tarball downloads executed natively on the host OS without containerization.
- **`env_nspawn`**: Light OS-level virtualization via systemd-nspawn and `machinectl` containers.
- **`env_incus`**: Incus daemon setup, BTRFS storage pool creation, and LXC/VM profile management.
- **`env_docker`**: Docker CE engine, `br_netfilter` loading, and Compose deployments using BTRFS storage drivers.
- **`env_kubernetes`**: K3s/Kubernetes node initialization, container runtime socket linkage, and CNI/overlay networking rules.

---

## Rebase Workflow Guidelines

To ensure updates to the core OS setup do not diverge across branches, operators must maintain a linear git history.

1. **OS Baseline Changes:** Commit base system updates directly to `main` (or feature branches merged into `main`).
2. **Propagating OS Updates:** Run periodic rebases on active service branches:

```bash
git checkout env_<target-stack>
git fetch origin
git rebase origin/main

```

3. **Branch Specificity:** Commits on `env_*` branches must strictly modify downstream playbooks, stack-specific sysctls, or runtime deployment tasks.

---

## Consequences

- **Positive:** Clear, modular separation between host operating system configurations and container runtime engines.
- **Positive:** Clean, linear Git history via rebase workflows, preventing complex merge-graph noise across runtime environments.
- **Positive:** Explicit isolation between native OS packages (`env_pkg`) and custom binary drops (`env_download`).
- **Positive:** Allows running individual orchestrators (like Incus vs. Kubernetes) on the exact same host hardware baseline with or without re-provisioning CachyOS.
- **Negative:** Requires strict developer discipline to avoid accidentally committing runtime-specific code onto `main` or encountering rebase merge conflicts during major baseline refactors.

---

## Links

- [ADR 0005: Separate Scope for Base OS and Workload Setup](https://www.google.com/search?q=./0005-separate-scope-for-base-os-and-workload-setup.md)
- [ADR 0011: Selection of CachyOS as Host OS](https://www.google.com/search?q=./0011-Selection-of-CachyOS-as-the-host-operating-system.md)ZZ
