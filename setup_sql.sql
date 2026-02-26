-- =====================================================
-- SQL Setup untuk IP Block Table
-- SOC Dashboard
-- =====================================================

-- Jika Anda lebih suka membuat tabel secara manual,
-- execute script ini di MySQL

-- Buat tabel ip_block
CREATE TABLE IF NOT EXISTS `ip_block` (
  `id` int NOT NULL AUTO_INCREMENT,
  `src_ip` varchar(45) NOT NULL,
  `reason` varchar(255) NOT NULL,
  `attack_count` int NOT NULL DEFAULT '0',
  `severity` varchar(20) NOT NULL,
  `status` varchar(20) NOT NULL DEFAULT 'pending',
  `security_group_id` varchar(50) DEFAULT NULL,
  `created_at` datetime NOT NULL,
  `blocked_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_src_ip` (`src_ip`),
  KEY `idx_status` (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Contoh data dummy untuk testing
INSERT INTO `ip_block` (`src_ip`, `reason`, `attack_count`, `severity`, `status`, `created_at`) VALUES
('192.168.1.100', 'Manual block - testing', 1, 'High', 'pending', NOW()),
('10.0.0.50', 'Brute force attack detected', 150, 'Critical', 'pending', NOW());

-- Verifikasi tabel dibuat
SHOW TABLES LIKE 'ip_block';

-- Lihat struktur tabel
DESCRIBE ip_block;
