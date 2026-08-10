# 4. Ansible for Declarative Agentless Automation

- **Status:** Accepted
- **Date:** 2026-08-09

## Context

Managing multiple Linux nodes using manual imperative shell scripts leads to drift, non-reproducible host states, and complex recovery paths.

## Decision

Adopt Ansible as the sole configuration management framework for cluster setup, OS tuning, and node teardown.

## Consequences

- **Positive:** Provides agentless management over standard SSH, strict task idempotency (`changed=0` on clean runs), and simple YAML-based task definitions.
- **Negative:** Requires managing OpenSSH authentication mechanics and Python dependency environments on the control laptop.
