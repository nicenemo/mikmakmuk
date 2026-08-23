# ADR 0015: Storing Unencrypted SSH Management Keys

* **Status:** Accepted
* **Date:** 2026-08-23
* **Deciders:** Hans Kruse

---

## Context and Problem Statement

The automation framework requires a dedicated SSH keypair (`id_ed25519_ansible`) generated on the local control node to manage the cluster. To protect this key from unauthorized extraction while at rest, initial implementation prototypes attempted to mandate passphrase encryption for the SSH private key, accompanied by dynamic secret retrieval using desktop secret services (such as KWallet and generic Secret Service DBus interfaces).

However, during prototyping, this approach introduced significant technical overhead and security risks:

* Playbook implementations required complex shell execution wrappers, temporary `askpass` scripts, and DBus bindings to handle passphrase generation, agent injection, and wallet storage.
* Automated handling of secrets in temporary scripts created secondary risk vectors, potentially leaking plain-text passphrases into local `/tmp` directories, environment variables, or shell execution traces.
* Integrating non-interactive Ansible executions with desktop secret managers (KWallet and DBus API integration) proved brittle across non-graphical sessions and background terminal executions.

Given that the primary control node already utilizes Full-Disk Encryption (FDE), we must decide whether the operational complexity and lingering security liabilities of SSH key passphrase management justify the risk mitigation, or if storing an unencrypted key on an FDE-protected volume is the superior alternative.

---

## Decision Drivers

* **Engineering Priority:** Avoid operational "side quests" that consume excessive setup time, prioritizing immediate project goals such as core Kubernetes, Incus, and bare-metal orchestration deployments.
* **Maintainability & Simplicity:** Minimize playbook complexity by eliminating reliance on external desktop services, complex shell hacks, and custom DBus API bindings.
* **Attacker Model & Risk Realism:** Recognize that the control node's primary physical threat vector (offline device theft) is already mitigated by Linux Full-Disk Encryption (LUKS).
* **Elimination of Secondary Leak Vectors:** Prevent transient plain-text secret exposures in system `/tmp` files, processes, or command execution traces caused by custom askpass wrappers.

---

## Decision Outcome

Chosen Option: **Store the generated Ansible SSH private key unencrypted on the control node filesystem (`~/.ssh/id_ed25519_ansible`), relying on host Full-Disk Encryption (FDE) and strict Unix permissions (`0600`) for access control.**

This decision explicitly accepts the risk of an unencrypted private key at rest on the active filesystem, provided the underlying volume is encrypted via LUKS.

---

## Consequences

* **Positive:** Drastically simplifies controller key setup (`controller-setup.yml`) and teardown (`controller-teardown.yml`) playbooks into declarative, native Ansible tasks.
* **Positive:** Eliminates brittle integrations with KWallet, secret-tool, and Secret Service DBus interfaces, ensuring playbooks run reliably across both GUI and headless SSH sessions.
* **Positive:** Removes security vulnerabilities associated with plain-text passphrases traversing process environments or temporary script files on disk.
* **Positive:** Reclaims critical engineering bandwidth, allowing development focus to shift immediately to downstream Kubernetes, Incus, and bare-metal infrastructure tasks.
* **Negative:** If an attacker gains active, unprivileged shell access to the running controller node while the LUKS volume is unlocked, they can read `~/.ssh/id_ed25519_ansible` directly without needing to crack a key passphrase.
* **Mitigation:** Access to the private key is constrained via POSIX permissions (`0600`) owned exclusively by the controller user. Physical theft of the device remains fully protected by FDE.

---

## Links

* [ADR 0004: Ansible for Declarative Agentless Automation](https://www.google.com/search?q=./0004-ansible-for-declarative-agentless-automation.md)
* [ADR 0005: Separate Scope for Base OS and Workload Setup](https://www.google.com/search?q=./0005-separate-scope-for-base-os-and-workload-setup.md)
* [ADR 0009: Requiring Password for Privilege Escalation](https://www.google.com/search?q=./0009-requiring-password-for-privilege-escalation.md)
