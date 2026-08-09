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
