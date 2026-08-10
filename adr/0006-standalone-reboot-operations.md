# 6. Standalone Reboot Operations

- **Status:** Accepted
- **Date:** 2026-08-09

## Context

Modifying kernel command-line parameters (`/etc/cmdline.d/`) and regenerating initramfs (`mkinitcpio -P`) requires a reboot to take effect. Automatically rebooting nodes inside the baseline setup playbook can cause unexpected service disruptions during routine playbook executions.

## Decision

Remove automatic reboot tasks from `base-setup.yml` and provide a dedicated, isolated playbook (`playbooks/reboot.yml`) with `--limit` support.

## Consequences

- **Positive:** Prevents unexpected node restarts during routine configuration runs; enables single-node rolling reboots during active maintenance windows.
- **Negative:** Administrative action is required to manual invoke `reboot.yml` after changing kernel options.
