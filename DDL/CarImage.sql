USE CarMarket;

CREATE TABLE IF NOT EXISTS CarImage (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    car_url_id BIGINT UNSIGNED NOT NULL,
    imageUrl VARCHAR(1000) NOT NULL,
    image_id VARCHAR(255) GENERATED ALWAYS AS (
        SUBSTRING_INDEX(SUBSTRING_INDEX(SUBSTRING_INDEX(imageUrl, '/', -1), '?', 1), '.', 1)
    ) STORED,
    UNIQUE KEY `unique_images` (image_id),
    FOREIGN KEY (car_url_id) REFERENCES CarWarehouse(url_id) ON DELETE CASCADE
);
