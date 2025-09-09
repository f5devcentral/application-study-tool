#!/bin/bash
set -e

echo "=== OTEL DB Initialization Script Started ==="

clickhouse client <<-EOSQL
    CREATE DATABASE IF NOT EXISTS otel;
EOSQL

# Create the null log table for incoming otel data
clickhouse client <<-EOSQL
    CREATE TABLE IF NOT EXISTS otel.otel_sslo_logs_null
    (
        Timestamp DateTime64(9) CODEC(Delta(8), ZSTD(1)),
        ObservedTimestamp DateTime64(9) CODEC(Delta(8), ZSTD(1)),
        TraceId String CODEC(ZSTD(1)),
        SpanId String CODEC(ZSTD(1)),
        TraceFlags UInt8,
        SeverityText LowCardinality(String) CODEC(ZSTD(1)),
        SeverityNumber UInt8,
        ServiceName LowCardinality(String) CODEC(ZSTD(1)),
        Body String CODEC(ZSTD(1)),
        ResourceSchemaUrl LowCardinality(String) CODEC(ZSTD(1)),
        ResourceAttributes Map(LowCardinality(String), String) CODEC(ZSTD(1)),
        ScopeSchemaUrl LowCardinality(String) CODEC(ZSTD(1)),
        ScopeName String CODEC(ZSTD(1)),
        ScopeVersion LowCardinality(String) CODEC(ZSTD(1)),
        ScopeAttributes Map(LowCardinality(String), String) CODEC(ZSTD(1)),
        LogAttributes Map(LowCardinality(String), String) CODEC(ZSTD(1)),
    )
    ENGINE = Null;
EOSQL


# Create the actual table which logs will be stored in
clickhouse client <<-EOSQL

    CREATE TABLE IF NOT EXISTS otel.sslo_logs
    (
        Timestamp DateTime,
        ObservedTimestamp DateTime,
        hostname String CODEC(ZSTD(1)),
        flow_id String CODEC(ZSTD(1)),
        vip String CODEC(ZSTD(1)),
        l4_protocol LowCardinality(String) CODEC(ZSTD(1)),
        src_ip String CODEC(ZSTD(1)),
        src_port UInt16,
        dst_ip String CODEC(ZSTD(1)),
        dst_port UInt16,
        client_ssl_protocol LowCardinality(String) CODEC(ZSTD(1)),
        client_ssl_cipher LowCardinality(String) CODEC(ZSTD(1)),
        server_ssl_protocol LowCardinality(String) CODEC(ZSTD(1)),
        server_ssl_cipher LowCardinality(String) CODEC(ZSTD(1)),
        l7_protocol LowCardinality(String) CODEC(ZSTD(1)),
        sslo_host String CODEC(ZSTD(1)),
        decryption_status LowCardinality(String) CODEC(ZSTD(1)),
        duration UInt64,
        service_path String CODEC(ZSTD(1)),
        client_bytes_in UInt64,
        client_bytes_out UInt64,
        server_bytes_in UInt64,
        server_bytes_out UInt64,
        client_tls_handshake LowCardinality(String) CODEC(ZSTD(1)),
        server_tls_handshake LowCardinality(String) CODEC(ZSTD(1)),
        reset_cause LowCardinality(String) CODEC(ZSTD(1)),
        policy_rule LowCardinality(String) CODEC(ZSTD(1)),
        url_category LowCardinality(String) CODEC(ZSTD(1)),
        ingress String CODEC(ZSTD(1)),
        egress String CODEC(ZSTD(1)),
    )
    ENGINE = MergeTree
    ORDER BY (Timestamp)
    TTL Timestamp + INTERVAL 24 HOUR;
EOSQL

# Create the Materialized View that populates the access log table from incoming
# null logs.
clickhouse client <<-EOSQL
    CREATE MATERIALIZED VIEW IF NOT EXISTS otel.sslo_logs_mv TO otel.sslo_logs AS
    SELECT  Timestamp::DateTime AS Timestamp,
    ObservedTimestamp::DateTime AS ObservedTimestamp,
    LogAttributes['hostname'] AS hostname,
    LogAttributes['flow_id'] AS flow_id,
    LogAttributes['vip'] AS vip,
    LogAttributes['l4_protocol'] AS l4_protocol,
    LogAttributes['src_ip'] AS src_ip,
    LogAttributes['src_port'] AS src_port,
    LogAttributes['dst_ip'] AS dst_ip,
    LogAttributes['dst_port'] AS dst_port,
    LogAttributes['client_ssl_protocol'] AS client_ssl_protocol,
    LogAttributes['client_ssl_cipher'] AS client_ssl_cipher,
    LogAttributes['server_ssl_protocol'] AS server_ssl_protocol,
    LogAttributes['server_ssl_cipher'] AS server_ssl_cipher,
    LogAttributes['l7_protocol'] AS l7_protocol,
    LogAttributes['sslo_host'] AS sslo_host,
    LogAttributes['decryption_status'] AS decryption_status,
    LogAttributes['duration'] AS duration,
    LogAttributes['service_path'] AS service_path,
    LogAttributes['client_bytes_in'] AS client_bytes_in,
    LogAttributes['client_bytes_out'] AS client_bytes_out,
    LogAttributes['server_bytes_in'] AS server_bytes_in,
    LogAttributes['server_bytes_out'] AS server_bytes_out,
    LogAttributes['client_tls_handshake'] AS client_tls_handshake,
    LogAttributes['server_tls_handshake'] AS server_tls_handshake,
    LogAttributes['reset_cause'] AS reset_cause,
    LogAttributes['policy_rule'] AS policy_rule,
    LogAttributes['url_category'] AS url_category,
    LogAttributes['ingress'] AS ingress,
    LogAttributes['egress'] AS egress
    FROM otel.otel_sslo_logs_null;
EOSQL
