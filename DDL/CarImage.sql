USE CarMarket;

CREATE TABLE IF NOT EXISTS CarImage (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    car_url_id BIGINT UNSIGNED NOT NULL,
    imageUrl VARCHAR(1000) NOT NULL,
    hash_512 CHAR(128) GENERATED ALWAYS AS (sha2(imageUrl, 512)) STORED,
    UNIQUE KEY `unique_images` (hash_512),
    FOREIGN KEY (car_url_id) REFERENCES CarWarehouse(url_id) ON DELETE CASCADE
);
