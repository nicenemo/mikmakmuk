# 9. Requiring Password for Privilege Escalation (No Passwordless Sudo)

* **Status:** Accepted
* **Date:** 2026-08-09

## Context

When running Ansible playbooks that require `root` access, entering a `sudo` password for every execution adds minor friction. A common homelab shortcut is to drop a `NOPASSWD: ALL` configuration into `/etc/sudoers.d/` for the automation user, allowing Ansible to run completely unattended. 

However, passwordless `sudo` creates a significant security risk. If the control laptop is compromised, or an SSH key is leaked, an attacker gains immediate, frictionless root access to the entire cluster.

## Decision

We will not configure passwordless `sudo` on the target nodes. Instead, we will rely on Ansible's `become_ask_pass = True` setting in `ansible.cfg`. 

## Consequences

* **Positive:** Maintains a strong security posture. Even if an SSH key is compromised, arbitrary root-level execution is blocked by the local password prompt.
* **Negative:** Requires the operator to manually enter the `sudo` password once at the start of any playbook run (e.g., `./setup.yml`).
