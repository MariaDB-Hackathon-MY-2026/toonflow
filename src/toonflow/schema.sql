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

CREATE TABLE IF NOT EXISTS toon_record_fields (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    payload_id VARCHAR(128) NOT NULL,
    field_path VARCHAR(255) NOT NULL,
    value_string TEXT NULL,
    value_number DOUBLE NULL,
    value_boolean BOOLEAN NULL,
    created_at DATETIME(6) NOT NULL,
    INDEX idx_field_path (field_path),
    INDEX idx_payload_field (payload_id, field_path),
    INDEX idx_field_string (field_path, value_string(191)),
    INDEX idx_field_number (field_path, value_number),
    CONSTRAINT fk_toon_record_fields_payload
        FOREIGN KEY (payload_id) REFERENCES toon_records(payload_id)
        ON DELETE CASCADE
);
