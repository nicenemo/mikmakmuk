# 7. CPU Undervolting Strategy and Microcode Lock Handling

* **Status:** Outdated
* **Date:** 2026-08-09

## Context

Mini-PC chassis (such as HP ProDesk 400/600/800 G4) experience thermal throttling under sustained heavy CPU workloads. While `intel-undervolt` can reduce power consumption and thermal output, Intel Plundervolt microcode updates locked Model Specific Registers (MSR `0x150`) across many 8th-Gen Coffee Lake BIOS releases.

## Decision

* Maintain a Jinja2 template (`templates/intel-undervolt.conf.j2`) for undervolt configuration management.
* Explicitly disable `intel-undervolt.service` (`enable false` in config, service `state: stopped`, `enabled: false`) across nodes where BIOS/microcode mitigations prevent MSR writes.

## Consequences

* **Positive:** Prevents `intel-undervolt.service` boot/systemd unit failures (`Values do not equal` / exit status 1) on nodes with locked voltage registers.
* **Negative:** Nodes with locked microcode run at factory voltage tables and rely purely on passive/active fan cooling.
