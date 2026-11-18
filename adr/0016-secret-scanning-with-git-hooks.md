# ADR 0016: Secret Scanning with Git Hooks

- **Status:** Accepted
- **Date:** 2026-11-18

## Context

The repository is public and manages SSH access, sudo rules and certificates for the cluster. A secret that reaches
GitHub has to be treated as leaked, even if the commit is removed later (see also ADR 0015 on the unencrypted
automation key, which lives in `~/.ssh` and not in the repository). The same hooks are used in the other playbook
repositories (kos, multiberry, samos).

## Decision

- A tracked `pre-commit` hook (`.githooks/pre-commit`) runs `gitleaks git --staged` and, because this repository has a
  `.yamllint`, `yamllint .`.
- A tracked `pre-push` hook runs `trufflehog` over the commits that are about to be pushed and fails on any finding.
- `.gitleaks.toml` extends the default ruleset, adds a rule for Ansible vault passwords and ignores `*.pub` files and
  lines that only reference a Jinja variable.
- `./githooks-setup.sh` sets `core.hooksPath` to `.githooks`, once per checkout. Both hooks refuse to run when their
  scanner is missing. Secrets belong in an encrypted Ansible vault or outside the repository (`*.vault*`, `.vault_pass`
  and `credentials/` are in `.gitignore`).

## Consequences

- **Positive:** a secret is caught before it enters history and again before it leaves the machine.
- **Negative:** hooks are not cloned automatically and `--no-verify` skips them, so a periodic scan of the full history
  is the safety net. `trufflehog` is not in the official Arch repositories (AUR `trufflehog-bin`).
