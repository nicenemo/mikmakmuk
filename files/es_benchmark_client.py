#!/usr/bin/env python3
"""
Elasticsearch 9 Replication & Payload Benchmark Runner
Externalized high-precision metric generator for Ansible
"""

import sys
import json
import time
import argparse
import warnings
from elasticsearch import Elasticsearch
from elasticsearch.exceptions import ElasticsearchWarning

# Suppress SSL warnings for local dev certificates
warnings.filterwarnings("ignore", category=ElasticsearchWarning)

def get_client(host: str, port: int, password: str) -> Elasticsearch:
    return Elasticsearch(
        [f"https://{host}:{port}"],
        basic_auth=("elastic", password),
        verify_certs=False,
        request_timeout=300
    )

def benchmark_bulk(es: Elasticsearch, index_name: str, doc_count: int, doc_size_bytes: int, batch_size: int):
    payload_str = "X" * doc_size_bytes
    doc_template = {"timestamp": "2026-11-08T10:00:00Z", "payload": payload_str}

    start_time = time.perf_counter()
    total_bytes = 0

    docs_remaining = doc_count
    while docs_remaining > 0:
        current_batch = min(docs_remaining, batch_size)
        operations = []
        for _ in range(current_batch):
            operations.append({"index": {"_index": index_name}})
            operations.append(doc_template)

        res = es.bulk(operations=operations, refresh=False)
        total_bytes += len(json.dumps(operations))
        docs_remaining -= current_batch

    es.indices.flush(index=index_name)
    end_time = time.perf_counter()

    duration = max(end_time - start_time, 0.001)
    payload_mb = round(total_bytes / (1024 * 1024), 2)
    throughput_mbs = round(payload_mb / duration, 2)
    throughput_gbps = round((throughput_mbs * 8) / 1024, 2)

    return {
        "doc_count": doc_count,
        "payload_mb": payload_mb,
        "duration_sec": round(duration, 3),
        "throughput_mbs": throughput_mbs,
        "throughput_gbps": throughput_gbps
    }

def benchmark_max_single(es: Elasticsearch, index_name: str):
    start_time = time.perf_counter()

    payload_45mb = "A" * (45 * 1024 * 1024)
    es.index(index=index_name, document={"title": "Doc1_45MB", "body": payload_45mb})

    payload_45mb_2 = "B" * (45 * 1024 * 1024)
    es.index(index=index_name, document={"title": "Doc2_45MB", "body": payload_45mb_2})

    es.indices.flush(index=index_name)
    end_time = time.perf_counter()

    duration = max(end_time - start_time, 0.001)
    total_bytes = 90 * 1024 * 1024
    payload_mb = round(total_bytes / (1024 * 1024), 2)
    throughput_mbs = round(payload_mb / duration, 2)
    throughput_gbps = round((throughput_mbs * 8) / 1024, 2)

    return {
        "doc_count": 2,
        "payload_mb": payload_mb,
        "duration_sec": round(duration, 3),
        "throughput_mbs": throughput_mbs,
        "throughput_gbps": throughput_gbps
    }

def main():
    parser = argparse.ArgumentParser(description="Elasticsearch 9 Replication Benchmark Client")
    parser.add_argument("--host", required=True)
    parser.add_argument("--port", type=int, default=9200)
    parser.add_argument("--password", required=True)
    parser.add_argument("--index", required=True)
    parser.add_argument("--mode", choices=["tiny", "medium", "large", "max", "max_docs"], required=True)
    args = parser.parse_args()

    es = get_client(args.host, args.port, args.password)

    if args.mode == "tiny":
        results = benchmark_bulk(es, args.index, doc_count=500000, doc_size_bytes=200, batch_size=5000)
    elif args.mode == "medium":
        results = benchmark_bulk(es, args.index, doc_count=100000, doc_size_bytes=2048, batch_size=2500)
    elif args.mode == "large":
        results = benchmark_bulk(es, args.index, doc_count=30000, doc_size_bytes=10240, batch_size=1000)
    elif args.mode in ["max", "max_docs"]:
        results = benchmark_max_single(es, args.index)

    print(json.dumps(results))

if __name__ == "__main__":
    main()
