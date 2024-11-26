-- Veritabanı içeriğini oluştur

CREATE TABLE IF NOT EXISTS sample_table (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50),
    value INT
);
CREATE TABLE IF NOT EXISTS processed_data (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50),
    value INT,
    combined_column VARCHAR(60)
);
CREATE TABLE IF NOT EXISTS third_table (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50),
    value INT,
    combined_column VARCHAR(60)
);

