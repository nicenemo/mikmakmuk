# 8. Disabling CPU Security Mitigations (Spectre/Meltdown)

* **Status:** Accepted
* **Date:** 2026-08-09

## Context

Intel's 8th-Generation Coffee Lake architecture is vulnerable to several hardware-level side-channel attacks, including Spectre, Meltdown, and L1TF. Mitigating these vulnerabilities at the kernel and microcode level incurs a severe performance penalty, significantly reducing context switch speeds, I/O performance, and overall CPU throughput.

Our cluster runs in an isolated, private homelab environment. Workloads consist of trusted, self-hosted applications and personal code, rather than multi-tenant, untrusted third-party code (like a public cloud provider would host).

## Decision

We will pass `mitigations=off` to the kernel command line in `/etc/cmdline.d/homelab-tuning.conf`.

## Consequences

* **Positive:** Unlocks maximum CPU and I/O performance for the i5-8500 and i5-8500T processors, recovering the 10% to 25% performance loss caused by security patches.
* **Negative:** Leaves the nodes theoretically vulnerable to speculative execution side-channel attacks. This is an acceptable risk given the strict physical and network isolation of the homelab and the absence of untrusted multi-tenant execution.
