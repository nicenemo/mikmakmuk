# ADR 0012: Manual Bootstrapping with Ventoy

- **Status:** Accepted
- **Date:** 2026-08-09
- **Deciders:** Hans Kruse
- **Technical Story:** Defining the interactive boot strategy and minimal manual bootstrap operations required before handing host management over to Ansible.

---

## Context and Problem Statement

To deploy the "Mik Mak Muk" cluster nodes (`mik`, `mak`, `muk`) on raw bare-metal hardware (HP Mini PCs), we need an efficient method to provision the base CachyOS operating system.

While fully automated cloud-init or PXE boot images exist, setting up dedicated PXE infrastructure for a small 3-node cluster introduces unnecessary complexity. Conversely, burning individual Linux ISOs repeatedly onto USB drives is slow and tedious. Furthermore, Ansible requires an operational OS environment with standard network configuration and an SSH daemon before it can execute remote playbooks.

We need a reproducible, low-overhead process to install a vanilla CachyOS OS on bare metal and perform the minimal manual commands required to expose SSH for Ansible.

---

## Decision Drivers

- **Minimal Setup Overhead:** Avoid maintaining dedicated PXE/iPXE boot infrastructure for only three nodes.
- **Standard ISO Usage:** Utilize the official, unmodified CachyOS desktop/minimal installer ISO without custom image baking.
- **Rapid Re-provisioning:** Ability to quickly re-flash a failed node using a single multi-boot USB drive.
- **Clear Automation Boundary:** Minimize manual interactive steps to only what is strictly required for network reachability and remote access (DHCP reservation, SSH daemon, and initial firewall rules).

---

## Considered Options

1. **Ventoy USB with Vanilla CachyOS ISO + Minimal Manual Bootstrap Commands**
2. **Dedicated PXE / Network Boot Server (e.g., Matchbox / Netboot.xyz)**
3. **Custom Pre-seeded ISO / Cloud-Init Image via DD/Etcher**

---

## Decision Outcome

Chosen Option: **Option 1 — Ventoy USB with Vanilla CachyOS ISO + Minimal Manual Bootstrap Commands**.

Ventoy allows maintaining a single multi-boot USB drive containing the stock CachyOS ISO. Nodes are booted manually via Ventoy to perform a standard CachyOS installation. Once installed, the operator executes a minimal set of explicit bootstrap commands on the target host to prepare it for Ansible automation.

### Bootstrap Workflow (as defined in `README.md`)

1. **Bare-Metal Installation:**
    - Boot host via Ventoy USB containing official CachyOS ISO.
    - Run vanilla installer selecting standard options (target NVMe disk, static hostname).

2. **Network Address Reservation:**
    - Configure static DHCP reservations on the router to fix node IP assignments:
      - `mik`: `192.168.105.2` (`mik.lab.local`)
      - `mak`: `192.168.105.3` (`mak.lab.local`)
      - `muk`: `192.168.105.4` (`muk.lab.local`)

3. **Manual Machine Bootstrap (Host Console):**
    - Enable OpenSSH daemon and local UFW firewall access for Ansible execution:

```bash
sudo systemctl enable --now sshd
sudo ufw allow 22/tcp
sudo ufw reload
```

4. **Handoff to Control Machine:**
    - Initiate initial setup playbook from the control machine using interactive SSH/Sudo credentials (`./setup.yml -k`).

---

## Positive Consequences

- **Simplicity:** No need to run or maintain dedicated PXE or network installation infrastructure.
- **Flexibility:** Ventoy allows updating or testing new CachyOS ISOs simply by dragging files onto the USB storage.
- **Clean Abstraction:** Manual steps are capped at under 2 minutes per node (enabling SSH and opening port 22), keeping the boundary between manual installation and automated Ansible playbooks crisp.

## Negative Consequences & Mitigation

- **Requires Physical Console Access:** Booting from USB and completing the GUI/CLI installer requires physical monitor/keyboard access or KVM-over-IP.
  - _Mitigation:_ Cluster nodes are physically accessible in a home lab environment; full OS re-installations are rare events.
- **Manual Error Risk:** Typo risk during manual console command execution.
  - _Mitigation:_ The manual commands are intentionally limited to 3 distinct lines (`systemctl` and `ufw` setup), which are documented directly in the primary `README.md`.

---

## Links

- [README.md - Quickstart & Execution](../README.md#quickstart--execution)
- [ADR 0004: Ansible Framework Choice](./0004-ansible-for-declarative-agentless-automation.md)
- [ADR 0005: Separate Scope for Base OS and Workload Setup](./0005-separate-scope-for-base-os-and-workload-setup.md)
