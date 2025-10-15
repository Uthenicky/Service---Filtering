CREATE TABLE message_logs (
    id SERIAL PRIMARY KEY,
    tenant_id VARCHAR(50) NOT NULL,
    from_number VARCHAR(20) NOT NULL,
    to_number VARCHAR(20) NOT NULL,
    original_text TEXT,
    normalized_text TEXT,
    sentiment JSONB,
    badwords JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indeks untuk tabel message_logs
CREATE INDEX ix_message_logs_tenant_id ON message_logs (tenant_id);
CREATE INDEX ix_message_logs_from_number ON message_logs (from_number);


CREATE TABLE customer_metrics (
    id SERIAL PRIMARY KEY,
    tenant_id VARCHAR(50) NOT NULL,
    message_log_id INT NOT NULL REFERENCES message_logs(id) ON DELETE CASCADE,
    from_number VARCHAR(20) NOT NULL,
    has_badwords BOOLEAN,
    sentiment_score INT DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indeks untuk tabel customer_metrics
CREATE INDEX ix_customer_metrics_tenant_wa_number ON customer_metrics (tenant_id, from_number);