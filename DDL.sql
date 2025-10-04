
CREATE TABLE message_logs (
    id SERIAL PRIMARY KEY,
    client_id VARCHAR(50) NOT NULL,
    from_number VARCHAR(20) NOT NULL,
    to_number VARCHAR(20) NOT NULL,
    original_text TEXT,
    normalized_text TEXT,
    sentiment JSONB,
    badwords JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX ix_message_logs_client_id ON message_logs (client_id);
CREATE INDEX ix_message_logs_from_number ON message_logs (from_number);
CREATE INDEX ix_message_logs_to_number ON message_logs (to_number);