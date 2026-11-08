#!/usr/bin/env ansible-playbook
---
- name: Master Elasticsearch Replication & Payload Size Benchmark
  hosts: cluster_nodes
  become: true
  vars:
    project_root: "{{ playbook_dir if not playbook_dir.endswith('playbooks') else playbook_dir ~ '/..' }}"
    test_index_tiny: "bench_replication_tiny_docs"
    test_index_medium: "bench_replication_medium_docs"
    test_index_large: "bench_replication_large_docs"
    test_index_max: "bench_replication_max_docs"
    es_elastic_password: "{{ lookup('ansible.builtin.password', project_root ~ '/credentials/elastic_password.txt length=24 chars=ascii_letters,digits') }}"
    mgmt_iface: "{{ ansible_facts['default_ipv4']['interface'] }}"

  tasks:
    # -------------------------------------------------------------------------
    # 1. Dynamic Interface & Dependency Setup
    # -------------------------------------------------------------------------
    - name: Ensure python-elasticsearch client package is installed via pacman
      community.general.pacman:
        name: python-elasticsearch
        state: present
        update_cache: true
      when: inventory_hostname == groups['cluster_nodes'][0]

    - name: Deploy external benchmark python script
      ansible.builtin.copy:
        src: "{{ project_root }}/files/es_benchmark_client.py"
        dest: /usr/local/bin/es_benchmark_client.py
        mode: '0755'
      when: inventory_hostname == groups['cluster_nodes'][0]

    - name: Discover physical 2.5 GbE USB interface
      ansible.builtin.set_fact:
        usb_iface: >-
          {{
            ansible_facts['interfaces']
            | reject('equalto', 'lo')
            | reject('equalto', mgmt_iface)
            | select('match', '^(eth|en|enp|wlx|usb).*')
            | list
            | first
          }}

    - name: Extract clean 2.5 GbE cluster IP
      ansible.builtin.set_fact:
        cluster_25g_ip: "{{ (hostvars[inventory_hostname]['cluster_ip'] | default(ansible_facts[usb_iface]['ipv4']['address'])) | regex_replace('/.*$', '') }}"

    # =========================================================================
    # PASS 1: TINY DOCUMENTS (~200 Bytes, Micro-Batches)
    # =========================================================================
    - name: Run Tiny Documents Benchmark Block
      block:
        - name: Setup index for tiny docs (3 shards, 1 replica)
          ansible.builtin.uri:
            url: "https://{{ elasticsearch_ip }}:9200/{{ test_index_tiny }}"
            method: PUT
            user: elastic
            password: "{{ es_elastic_password }}"
            force_basic_auth: true
            validate_certs: false
            body_format: json
            body:
              settings:
                number_of_shards: 3
                number_of_replicas: 1
                refresh_interval: "1s"
            status_code: [200]
          run_once: true

        - name: Read initial 2.5 GbE stats (Pass 1)
          ansible.builtin.command: "cat /sys/class/net/{{ usb_iface }}/statistics/tx_bytes"
          register: tx_tiny_start
          changed_when: false

        - name: Record start time (Pass 1)
          ansible.builtin.set_fact:
            start_tiny: "{{ ansible_facts['date_time']['epoch'] }}"

        - name: Ingest Micro-Bulk Batches via Native Ansible URI (~200B Docs)
          ansible.builtin.uri:
            url: "https://{{ elasticsearch_ip }}:9200/{{ test_index_tiny }}/_bulk"
            method: POST
            user: elastic
            password: "{{ es_elastic_password }}"
            force_basic_auth: true
            validate_certs: false
            headers:
              Content-Type: "application/x-ndjson"
            body: "{{ lookup('template', project_root ~ '/templates/es_bulk_payload.j2', template_vars={'doc_count': 500, 'doc_size_bytes': 100, 'fill_char': 'T'}) }}"
            status_code: [200]
          loop: "{{ range(0, 40) | list }}"
          when: inventory_hostname == groups['cluster_nodes'][0]

        - name: Flush tiny docs index to disk
          ansible.builtin.uri:
            url: "https://{{ elasticsearch_ip }}:9200/{{ test_index_tiny }}/_flush"
            method: POST
            user: elastic
            password: "{{ es_elastic_password }}"
            force_basic_auth: true
            validate_certs: false
            status_code: [200]
          run_once: true

        - name: Record end time (Pass 1)
          ansible.builtin.set_fact:
            end_tiny: "{{ ansible_facts['date_time']['epoch'] }}"

        - name: Read final 2.5 GbE stats (Pass 1)
          ansible.builtin.command: "cat /sys/class/net/{{ usb_iface }}/statistics/tx_bytes"
          register: tx_tiny_end
          changed_when: false

        - name: Compute Pass 1 TX Megabytes
          ansible.builtin.set_fact:
            tx_tiny_mb: "{{ ((tx_tiny_end.stdout | int - tx_tiny_start.stdout | int) / 1024 / 1024) | round(2) }}"

    # =========================================================================
    # PASS 2: MEDIUM DOCUMENTS (~2 KB, 5MB Batches)
    # =========================================================================
    - name: Run Medium Documents Benchmark Block
      block:
        - name: Setup index for medium docs (3 shards, 1 replica)
          ansible.builtin.uri:
            url: "https://{{ elasticsearch_ip }}:9200/{{ test_index_medium }}"
            method: PUT
            user: elastic
            password: "{{ es_elastic_password }}"
            force_basic_auth: true
            validate_certs: false
            body_format: json
            body:
              settings:
                number_of_shards: 3
                number_of_replicas: 1
                refresh_interval: "10s"
            status_code: [200]
          run_once: true

        - name: Read initial 2.5 GbE stats (Pass 2)
          ansible.builtin.command: "cat /sys/class/net/{{ usb_iface }}/statistics/tx_bytes"
          register: tx_medium_start
          changed_when: false

        - name: Record start time (Pass 2)
          ansible.builtin.set_fact:
            start_medium: "{{ ansible_facts['date_time']['epoch'] }}"

        - name: Ingest Medium Bulk Batches via Native Ansible URI (~2KB Docs)
          ansible.builtin.uri:
            url: "https://{{ elasticsearch_ip }}:9200/{{ test_index_medium }}/_bulk"
            method: POST
            user: elastic
            password: "{{ es_elastic_password }}"
            force_basic_auth: true
            validate_certs: false
            headers:
              Content-Type: "application/x-ndjson"
            body: "{{ lookup('template', project_root ~ '/templates/es_bulk_payload.j2', template_vars={'doc_count': 1000, 'doc_size_bytes': 2048, 'fill_char': 'M'}) }}"
            status_code: [200]
          loop: "{{ range(0, 15) | list }}"
          when: inventory_hostname == groups['cluster_nodes'][0]

        - name: Flush medium docs index to disk
          ansible.builtin.uri:
            url: "https://{{ elasticsearch_ip }}:9200/{{ test_index_medium }}/_flush"
            method: POST
            user: elastic
            password: "{{ es_elastic_password }}"
            force_basic_auth: true
            validate_certs: false
            status_code: [200]
          run_once: true

        - name: Record end time (Pass 2)
          ansible.builtin.set_fact:
            end_medium: "{{ ansible_facts['date_time']['epoch'] }}"

        - name: Read final 2.5 GbE stats (Pass 2)
          ansible.builtin.command: "cat /sys/class/net/{{ usb_iface }}/statistics/tx_bytes"
          register: tx_medium_end
          changed_when: false

        - name: Compute Pass 2 TX Megabytes
          ansible.builtin.set_fact:
            tx_medium_mb: "{{ ((tx_medium_end.stdout | int - tx_medium_start.stdout | int) / 1024 / 1024) | round(2) }}"

    # =========================================================================
    # PASS 3: LARGE DOCUMENTS (~10 KB, 10MB Batches)
    # =========================================================================
    - name: Run Large Documents Benchmark Block
      block:
        - name: Setup index for large docs (3 shards, 1 replica)
          ansible.builtin.uri:
            url: "https://{{ elasticsearch_ip }}:9200/{{ test_index_large }}"
            method: PUT
            user: elastic
            password: "{{ es_elastic_password }}"
            force_basic_auth: true
            validate_certs: false
            body_format: json
            body:
              settings:
                number_of_shards: 3
                number_of_replicas: 1
                refresh_interval: "30s"
            status_code: [200]
          run_once: true

        - name: Read initial 2.5 GbE stats (Pass 3)
          ansible.builtin.command: "cat /sys/class/net/{{ usb_iface }}/statistics/tx_bytes"
          register: tx_large_start
          changed_when: false

        - name: Record start time (Pass 3)
          ansible.builtin.set_fact:
            start_large: "{{ ansible_facts['date_time']['epoch'] }}"

        - name: Ingest Large Bulk Batches via Native Ansible URI (~10KB Docs)
          ansible.builtin.uri:
            url: "https://{{ elasticsearch_ip }}:9200/{{ test_index_large }}/_bulk"
            method: POST
            user: elastic
            password: "{{ es_elastic_password }}"
            force_basic_auth: true
            validate_certs: false
            headers:
              Content-Type: "application/x-ndjson"
            body: "{{ lookup('template', project_root ~ '/templates/es_bulk_payload.j2', template_vars={'doc_count': 500, 'doc_size_bytes': 10240, 'fill_char': 'Z'}) }}"
            status_code: [200]
          loop: "{{ range(0, 15) | list }}"
          when: inventory_hostname == groups['cluster_nodes'][0]

        - name: Flush large docs index to disk
          ansible.builtin.uri:
            url: "https://{{ elasticsearch_ip }}:9200/{{ test_index_large }}/_flush"
            method: POST
            user: elastic
            password: "{{ es_elastic_password }}"
            force_basic_auth: true
            validate_certs: false
            status_code: [200]
          run_once: true

        - name: Record end time (Pass 3)
          ansible.builtin.set_fact:
            end_large: "{{ ansible_facts['date_time']['epoch'] }}"

        - name: Read final 2.5 GbE stats (Pass 3)
          ansible.builtin.command: "cat /sys/class/net/{{ usb_iface }}/statistics/tx_bytes"
          register: tx_large_end
          changed_when: false

        - name: Compute Pass 3 TX Megabytes
          ansible.builtin.set_fact:
            tx_large_mb: "{{ ((tx_large_end.stdout | int - tx_large_start.stdout | int) / 1024 / 1024) | round(2) }}"

    # =========================================================================
    # PASS 4: MAX SINGLE-DOC INGEST (External ES 9 Python Client Script)
    # =========================================================================
    - name: Run Max Single-Document Benchmark Block
      block:
        - name: Setup index for max single doc (3 shards, 1 replica)
          ansible.builtin.uri:
            url: "https://{{ elasticsearch_ip }}:9200/{{ test_index_max }}"
            method: PUT
            user: elastic
            password: "{{ es_elastic_password }}"
            force_basic_auth: true
            validate_certs: false
            body_format: json
            body:
              settings:
                number_of_shards: 3
                number_of_replicas: 1
                refresh_interval: "30s"
            status_code: [200]
          run_once: true

        - name: Read initial 2.5 GbE stats (Pass 4)
          ansible.builtin.command: "cat /sys/class/net/{{ usb_iface }}/statistics/tx_bytes"
          register: tx_max_start
          changed_when: false

        - name: Record start time (Pass 4)
          ansible.builtin.set_fact:
            start_max: "{{ ansible_facts['date_time']['epoch'] }}"

        - name: Execute external ES 9 benchmark client for 50MB and 95MB single documents
          ansible.builtin.command:
            cmd: >
              /usr/local/bin/es_benchmark_client.py
              --host "{{ elasticsearch_ip }}"
              --port 9200
              --password "{{ es_elastic_password }}"
              --index "{{ test_index_max }}"
              --mode max_docs
          when: inventory_hostname == groups['cluster_nodes'][0]
          changed_when: true

        - name: Flush max docs index to disk
          ansible.builtin.uri:
            url: "https://{{ elasticsearch_ip }}:9200/{{ test_index_max }}/_flush"
            method: POST
            user: elastic
            password: "{{ es_elastic_password }}"
            force_basic_auth: true
            validate_certs: false
            status_code: [200]
          run_once: true

        - name: Record end time (Pass 4)
          ansible.builtin.set_fact:
            end_max: "{{ ansible_facts['date_time']['epoch'] }}"

        - name: Read final 2.5 GbE stats (Pass 4)
          ansible.builtin.command: "cat /sys/class/net/{{ usb_iface }}/statistics/tx_bytes"
          register: tx_max_end
          changed_when: false

        - name: Compute Pass 4 TX Megabytes
          ansible.builtin.set_fact:
            tx_max_mb: "{{ ((tx_max_end.stdout | int - tx_max_start.stdout | int) / 1024 / 1024) | round(2) }}"

    # -------------------------------------------------------------------------
    # 5. Summary Output (Executed on Primary Generator Node mik)
    # -------------------------------------------------------------------------
    - name: Display Comprehensive Benchmark Summary Report
      ansible.builtin.debug:
        msg:
          - "========================================================================="
          - "   ELASTICSEARCH REPLICATION BENCHMARK: COMPLETE PAYLOAD PROFILE REPORT   "
          - "========================================================================="
          - "PASS 1: TINY DOCUMENTS (~200B per doc, Micro-Batches)"
          - "  Total Transmitted Payload : {{ tx_tiny_mb }} MB"
          - "  Elapsed Duration          : {{ (end_tiny | int) - (start_tiny | int) }} seconds"
          - "  Effective Speed           : {{ ((tx_tiny_mb | float) / ((end_tiny | int) - (start_tiny | int) + 0.001)) | round(2) }} MB/s"
          - "-------------------------------------------------------------------------"
          - "PASS 2: MEDIUM DOCUMENTS (~2KB per doc, 5MB Batches)"
          - "  Total Transmitted Payload : {{ tx_medium_mb }} MB"
          - "  Elapsed Duration          : {{ (end_medium | int) - (start_medium | int) }} seconds"
          - "  Effective Speed           : {{ ((tx_medium_mb | float) / ((end_medium | int) - (start_medium | int) + 0.001)) | round(2) }} MB/s"
          - "-------------------------------------------------------------------------"
          - "PASS 3: LARGE DOCUMENTS (~10KB per doc, 10MB Batches)"
          - "  Total Transmitted Payload : {{ tx_large_mb }} MB"
          - "  Elapsed Duration          : {{ (end_large | int) - (start_large | int) }} seconds"
          - "  Effective Speed           : {{ ((tx_large_mb | float) / ((end_large | int) - (start_large | int) + 0.001)) | round(2) }} MB/s"
          - "-------------------------------------------------------------------------"
          - "PASS 4: MAX SINGLE-DOC INGEST (50MB + 95MB Single Documents)"
          - "  Total Transmitted Payload : {{ tx_max_mb }} MB"
          - "  Elapsed Duration          : {{ (end_max | int) - (start_max | int) }} seconds"
          - "  Effective Speed           : {{ ((tx_max_mb | float) / ((end_max | int) - (start_max | int) + 0.001)) | round(2) }} MB/s"
          - "========================================================================="
      when: inventory_hostname == groups['cluster_nodes'][0]

    # -------------------------------------------------------------------------
    # 6. Teardown
    # -------------------------------------------------------------------------
    - name: Purge benchmark indices
      ansible.builtin.uri:
        url: "https://{{ elasticsearch_ip }}:9200/{{ item }}"
        method: DELETE
        user: elastic
        password: "{{ es_elastic_password }}"
        force_basic_auth: true
        validate_certs: false
        status_code: [200, 404]
      loop:
        - "{{ test_index_tiny }}"
        - "{{ test_index_medium }}"
        - "{{ test_index_large }}"
        - "{{ test_index_max }}"
      run_once: true
