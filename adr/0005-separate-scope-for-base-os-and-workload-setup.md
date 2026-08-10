# 5. Separate Scope for Base OS and Workload Setup

- **Status:** Accepted
- **Date:** 2026-08-09

## Context

Mixing base kernel tuning (driver installs, power parameters, CPU mitigations) with orchestration layer setup (Kubernetes, Docker, Incus) creates bloated playbooks that break when changing orchestrators.

## Decision

Decouple hardware platform tuning from workload orchestrators. This repository strictly manages OS and hardware baseline configurations. Downstream container networking (e.g., `overlay`, `br_netfilter`, sysctl IP forwarding) belongs in dedicated downstream repositories or branches.

## Consequences

- **Positive:** The base OS automation remains agnostic to future orchestrator choices (Kubernetes, Incus, systemd-nspawn, Docker).
- **Negative:** Requires running separate playbooks sequentially when bootstrapping new nodes from scratch.
