# AGENTS.md — Contributor Guidelines for AI Assistants

This repository contains declarative, agentless Ansible playbooks, configuration files, and documentation for managing **The Mik Mak Muk Cluster** (a 3-node bare-metal homelab built on HP Mini PCs running CachyOS).

## 1. Project Structure & File Conventions

Always respect the following project directory structure:

```text
mikmakmuk/
├── playbooks/
│   ├── files/               # Static drop-in files (configs, systemd units)
│   │   ├── homelab-tuning.conf
│   │   ├── igpu.conf
│   │   └── powertop.service
│   ├── base-setup.yml       # Primary host provisioning playbook
│   ├── base-teardown.yml    # Reversion/cleanup playbook
│   └── reboot.yml           # Rolling single-node reboot maintenance playbook
├── blogpost.md              # Hugo static site blog post
└── AGENTS.md                # AI instructions (this file)
```
