# ADR 0012: Manual Bootstrapping with Ventoy

* **Status:** Accepted
* **Date:** 2026-08-09
* **Deciders:** Hans Kruse
* **Technical Story:** Defining the interactive boot strategy and minimal manual bootstrap operations required before handing host management over to Ansible.

---

## Context and Problem Statement

To deploy the "Mik Mak Muk" cluster nodes (`mik`, `mak`, `muk`) on raw bare-metal hardware (HP Mini PCs), we need an efficient method to provision the base CachyOS operating system[cite: 1]. 

While fully automated cloud-init or PXE boot images exist, setting up dedicated PXE infrastructure for a small 3-node cluster introduces unnecessary complexity. Conversely, burning individual Linux ISOs repeatedly onto USB drives is slow and tedious. Furthermore, Ansible requires an operational OS environment with standard network configuration and an SSH daemon before it can execute remote playbooks[cite: 1].

We need a reproducible, low-overhead process to install a vanilla CachyOS OS on bare metal and perform the minimal manual commands required to expose SSH for Ansible[cite: 1].

---

## Decision Drivers

* **Minimal Setup Overhead:** Avoid maintaining dedicated PXE/iPXE boot infrastructure for only three nodes.
* **Standard ISO Usage:** Utilize the official, unmodified CachyOS desktop/minimal installer ISO without custom image baking.
* **Rapid Re-provisioning:** Ability to quickly re-flash a failed node using a single multi-boot USB drive.
* **Clear Automation Boundary:** Minimize manual interactive steps to only what is strictly required for network reachability and remote access (DHCP reservation, SSH daemon, and initial firewall rules)[cite: 1].

---

## Considered Options

1. **Ventoy USB with Vanilla CachyOS ISO + Minimal Manual Bootstrap Commands**
2. **Dedicated PXE / Network Boot Server (e.g., Matchbox / Netboot.xyz)**
3. **Custom Pre-seeded ISO / Cloud-Init Image via DD/Etcher**

---

## Decision Outcome

Chosen Option: **Option 1 — Ventoy USB with Vanilla CachyOS ISO + Minimal Manual Bootstrap Commands**[cite: 1].

Ventoy allows maintaining a single multi-boot USB drive containing the stock CachyOS ISO[cite: 1]. Nodes are booted manually via Ventoy to perform a standard CachyOS installation[cite: 1]. Once installed, the operator executes a minimal set of explicit bootstrap commands on the target host to prepare it for Ansible automation[cite: 1].

### Bootstrap Workflow (as defined in `README.md`)

1. **Bare-Metal Installation:**
   * Boot host via Ventoy USB containing official CachyOS ISO[cite: 1].
   * Run vanilla installer selecting standard options (target NVMe disk, static hostname)[cite: 1].

2. **Network Address Reservation:**
   * Configure static DHCP reservations on the router to fix node IP assignments[cite: 1]:
     * `mik`: `192.168.105.2` (`mik.lab.local`)[cite: 1]
     * `mak`: `192.168.105.3` (`mak.lab.local`)[cite: 1]
     * `muk`: `192.168.105.4` (`muk.lab.local`)[cite: 1]

3. **Manual Machine Bootstrap (Host Console):**
   * Enable OpenSSH daemon and local UFW firewall access for Ansible execution[cite: 1]:
     ```bash
     sudo systemctl enable --now sshd
     sudo ufw allow 22/tcp
     sudo ufw reload
     ```[cite: 1]

4. **Handoff to Control Machine:**
   * Initiate initial setup playbook from the control machine using interactive SSH/Sudo credentials (`./setup.yml -k`)[cite: 1].

---

## Positive Consequences

* **Simplicity:** No need to run or maintain dedicated PXE or network installation infrastructure.
* **Flexibility:** Ventoy allows updating or testing new CachyOS ISOs simply by dragging files onto the USB storage[cite: 1].
* **Clean Abstraction:** Manual steps are capped at under 2 minutes per node (enabling SSH and opening port 22), keeping the boundary between manual installation and automated Ansible playbooks crisp[cite: 1].

## Negative Consequences & Mitigation

* **Requires Physical Console Access:** Booting from USB and completing the GUI/CLI installer requires physical monitor/keyboard access or KVM-over-IP.
  * *Mitigation:* Cluster nodes are physically accessible in a home lab environment; full OS re-installations are rare events.
* **Manual Error Risk:** Typo risk during manual console command execution.
  * *Mitigation:* The manual commands are intentionally limited to 3 distinct lines (`systemctl` and `ufw` setup), which are documented directly in the primary `README.md`[cite: 1].

---

## Links

* [README.md - Quickstart & Execution](../README.md#quickstart--execution)[cite: 1]
* [ADR 0004: Ansible Framework Choice](./0004-ansible-for-declarative-agentless-automation.md)[cite: 1]
* [ADR 0005: Separate Scope for Base OS and Workload Setup](./0005-separate-scope-for-base-os-and-workload-setup.md)[cite: 1]
