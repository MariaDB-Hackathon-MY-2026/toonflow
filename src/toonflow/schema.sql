CREATE TABLE IF NOT EXISTS toon_records (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    payload_id VARCHAR(128) NOT NULL UNIQUE,
    source VARCHAR(128) NOT NULL,
    original_json JSON NOT NULL,
    toon_payload LONGTEXT NOT NULL,
    extracted_fields JSON NOT NULL,
    status VARCHAR(32) NOT NULL,
    validation_errors JSON NOT NULL,
    validation_warnings JSON NOT NULL,
    created_at DATETIME(6) NOT NULL,
    INDEX idx_payload_id (payload_id),
    INDEX idx_source (source),
    INDEX idx_status (status),
    INDEX idx_created_at (created_at)
);
