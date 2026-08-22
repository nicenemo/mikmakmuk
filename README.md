# The Mik Mak Muk Cluster

This repository provides the baseline Ansible automation for a 3-node HP EliteDesk/ProDesk Mini cluster (`mik`, `mak`, `muk`).

It manages a **pure hardware and OS base setup** on CachyOS—optimizing kernel parameters, GPU video acceleration, and NVMe power states at the host layer before deploying container or orchestration workloads.

---

## Hardware Overview

| Hostname | Model                    | CPU                  | RAM   | Primary Role                     |
| :------- | :----------------------- | :------------------- | :---- | :------------------------------- |
| **mik**  | HP EliteDesk 800 Mini G4 | Intel i5-8500 (65W)  | 64 GB | Primary Master / Heavy Workloads |
| **mak**  | HP ProDesk 600 Mini G4   | Intel i5-8500T (35W) | 32 GB | Worker Node                      |
| **muk**  | HP ProDesk 400 Mini G4   | Intel i5-8500T (35W) | 16 GB | Worker Node / Ingress            |

For physical mounting, storage layout, networking, and hardware design rationales, see the [Architecture Decision Records (ADRs)](./adr/).

---

## Architecture Decision Records (ADRs)

Design choices and hardware constraints are tracked in the [`adr/`](./adr/) directory:

- [ADR 0001: Record Architecture Decisions](./adr/0001-record-architecture-decisions.md)
- [ADR 0002: Storage Layout & NVMe Boot Strategy](./adr/0002-storage-layout-and-nvme-only-boot.md)
- [ADR 0003: Under-Desk Sleeve Mounting](./adr/0003-physical-desk-sleeve-mounting.md)
- [ADR 0004: Ansible Framework Choice](./adr/0004-ansible-for-declarative-agentless-automation.md)
- [ADR 0005: Decoupling Base OS from Workloads](./adr/0005-separate-scope-for-base-os-and-workload-setup.md)
- [ADR 0006: Standalone Reboot Operations](./adr/0006-standalone-reboot-operations.md)
- [ADR 0007: CPU Undervolting & Microcode Lock Handling](./adr/0007-cpu-undervolting-strategy.md)
- [ADR 0008: Disabling CPU Security Mitigations](./adr/0008-disabling-cpu-security-mitigations.md)
- [ADR 0009: Requiring Password for Privilege Escalation](./adr/0009-requiring-password-for-privilege-escalation.md)
- [ADR 0010: Removing Intel Undervolting and Thermald from Project Configuration](./adr/0010-disabling-intel-undervolting-and-thermald.md)
- [ADR 0011: Selection of CachyOS as the Host Operating System](./adr/0011-Selection-of-CachyOS-as-the-host-operating-system.md)
- [ADR 0012: Manual Boostrapping with Ventoy](./adr/0012-Manual-bootstrapping-with-Ventoy.md)
- [ADR 0013: Renaming Hostnames to Mik, Mak, Muk](./adr/0013-Renaming-host-names-to-mik-mak-muk.md)
- [ADR 0014: Git Branching Strategy for Service Isolation](./adr/0014-git-branching-strategy.md)

---

## Quickstart & Execution

### 1. Control Laptop Setup

Install dependencies on your Arch/CachyOS control laptop:

```bash
sudo pacman -Syu --noconfirm ansible-core ansible-lint git python-paramiko sshpass
ansible-galaxy collection install community.general ansible.posix yamllint ansible-lint markdownlint-cli2 prettier editorconfig-checker 
```

## 2. Physical Node Bootstrap

Install minimal CachyOS via Ventoy USB on each host.

Set static DHCP reservations on your router:

- **mik:** 192.168.105.2
- **mak:** 192.168.105.3
- **muk:** 192.168.105.4

### 2. Physical Node Bootstrap

1. Install minimal CachyOS via Ventoy USB on each host.
2. Set static DHCP reservations and optionally DNS a records on your router:
    - **mik:** `192.168.105.2` (`mik.lab.local`)
    - **mak:** `192.168.105.3` (`mak.lab.local`)
    - **muk:** `192.168.105.4` (`muk.lab.local`)

### 3. Enable SSH daemon and configure local firewall access on each node:

```bash
sudo systemctl enable --now sshd
sudo ufw allow 22/tcp
sudo ufw reload
```

## 3. Running Playbooks

Management is split into two phases: **One-time Management User Provisioning** and **Routine Cluster Operations**.

### Phase A: Management User Setup / Teardown (Run Once)

The dedicated Ansible management user (`myansibleuser`) and SSH keys must be bootstrapped using your personal account (`bootstrap_user: kruse`). 

> **Important (PAM Lockout Prevention):** Both bootstrap and teardown playbooks use a specialized shebang (`ANSIBLE_SSH_CONTROL_PATH=none`). This temporarily disables SSH socket multiplexing for user setup tasks to prevent SSH connection socket caching from triggering rapid `pam_faillock` account lockouts on CachyOS/Arch.

* **Provision Management User:**
  `./ansible-user-setup.yml -K`
  *(Prompts once for your user's sudo password to create `myansibleuser`, copy SSH public keys, and configure passwordless sudo)*.

* **Teardown Management User:**
  `./ansible-user-teardown.yml -K`
  *(Removes `myansibleuser`, its `/etc/sudoers.d/` rule, and local SSH control keys)*.

### Phase B: Cluster Configuration & Operations

Once the management user is provisioned, standard maintenance runs passwordlessly via `myansibleuser` over persistent SSH multiplexing.

# Apply Base OS Setup & Tuning (Fully automated, passwordless)
./setup.yml

# Cluster rolling reboot (reboots one node at a time)
ansible-playbook playbooks/reboot.yml

# Reboot a single specific node
ansible-playbook playbooks/reboot.yml --limit muk

# Teardown / Revert base system configurations
./teardown.yml


## 4 Rationale: Dedicated Automation Lifecycle

Minimal base OS installs lack a standardized identity for background automation. Operating directly through personal user accounts for cluster tasks introduces clear security and reliability risks:

* **Access Decoupling:** Personal SSH keys should never double as service credentials. Provisioning a dedicated keypair for `myansibleuser` isolates interactive admin access from continuous integration and automation.


* **Scoped Escalation:** Interactive accounts remain protected by mandatory password checks for `sudo`. Giving `myansibleuser` explicit `NOPASSWD` rights enables non-interactive, unattended playbooks to complete without breaking system security for human operators.


* **Ephemeral Footprint:** The combination of `ansible-user-setup.yml` and `ansible-user-teardown.yml` allows management credentials to be provisioned on demand and purged completely whenever a node is decommissioned, keeping the attack surface minimal.


## 5 What Base Setup Applies

- **SSH Key Deployment:** Discovers local `~/.ssh/*.pub` keys on your control machine and provisions `authorized_keys` on target hosts ([OpenSSH Specification](https://www.openssh.com/manual.html)).
- **Package & Keyring Maintenance:** Updates Arch and CachyOS keyrings, syncs system packages (`pacman -Syu`), and installs hardware drivers (`intel-media-driver`, `libva-intel-driver`, `mesa`) ([Arch Wiki: VA-API](https://wiki.archlinux.org/title/Hardware_video_acceleration)).
- **Firewall Baseline:** Ensures standard UFW rules allow SSH access (`22/tcp`) on active interfaces ([Uncomplicated Firewall / Canonical](https://launchpad.net/ufw)).
- **Kernel Parameters (`/etc/cmdline.d/homelab-tuning.conf`):**
  - `mitigations=off`: Disables CPU speculative execution side-channel mitigations for maximum Coffee Lake performance ([Linux Kernel Documentation: Spectre/Meltdown Mitigations](https://www.kernel.org/doc/html/latest/admin-guide/hw-vuln/spectre.html)).
  - `i915.enable_guc=3`: Enables GuC (Graphics Microcontroller) and HuC (HEVC/H265 microcontroller) firmware for hardware video decoding and offloaded GPU scheduling ([Linux Kernel i915 Graphics Driver Docs](https://www.kernel.org/doc/html/latest/gpu/i915.html)).
  - `i915.enable_fbc=1`: Enables Frame Buffer Compression to save memory bandwidth and reduce power draw ([Intel Graphics Documentation](https://01.org/linuxgraphics)).
  - `intel_pstate=active`: Sets the active CPU performance scaling driver ([Linux Kernel CPU Performance Scaling Docs](https://www.kernel.org/doc/html/latest/admin-guide/pm/intel-pstate.html)).
  - `nvme_core.default_ps_max_latency_us=0`: Disables deep NVMe power-saving states to eliminate storage I/O latency and PCI bus disconnects ([Linux Kernel NVMe Driver Parameters](https://www.kernel.org/doc/html/latest/admin-guide/kernel-parameters.html)).
- **GPU Module:** Loads the `i915` kernel module on boot ([Arch Wiki: Kernel Modules](https://wiki.archlinux.org/title/Kernel_module)).
- **Disabled Undervolting:** Deploys `templates/intel-undervolt.conf.j2` with `enable false` and ensures `intel-undervolt.service` is stopped to prevent systemd service failures caused by HP BIOS microcode locks ([Intel Plundervolt Vulnerability / INTEL-SA-00289](https://www.intel.com/content/www/us/en/security-center/advisory/intel-sa-00289.html)).


## 6. Troubleshooting: PAM Lockouts
CachyOS enforces strict authentication limits via pam_faillock. Rapid connection attempts or password mismatches will temporarily lock accounts out of sudo privilege escalation, even while SSH key logins continue to work seamlessly.

1. Diagnosing Lockouts

Check active lockouts on a target host:

sudo faillock
sudo faillock --user kruse

2. Clearing Lockouts

Clear authentication counters directly on a host:

sudo faillock --reset
sudo faillock --user kruse --reset

3. Prevention

Always execute bootstrap and teardown operations using the repository's provided playbooks (./ansible-user-setup.yml and ./ansible-user-teardown.yml). Their built-in shebang disables SSH multiplexing socket caching (ANSIBLE_SSH_CONTROL_PATH=none), preventing SSH reuse from triggering rapid PAM rate limits.
