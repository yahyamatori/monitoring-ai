-- =====================================================
-- SQL untuk membuat tabel instance_mapping
-- SOC Dashboard
-- =====================================================

CREATE TABLE IF NOT EXISTS `instance_mapping` (
  `id` int NOT NULL AUTO_INCREMENT,
  `hostname` varchar(255) NOT NULL,
  `instance_id` varchar(50) NOT NULL,
  `public_ip` varchar(45) DEFAULT NULL,
  `private_ip` varchar(45) DEFAULT NULL,
  `security_group_id` varchar(50) NOT NULL,
  `security_group_name` varchar(100) DEFAULT NULL,
  `region_id` varchar(50) DEFAULT 'ap-southeast-3',
  `last_updated` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `is_active` tinyint(1) DEFAULT '1',
  PRIMARY KEY (`id`),
  UNIQUE KEY `hostname` (`hostname`),
  KEY `idx_security_group_id` (`security_group_id`),
  KEY `idx_is_active` (`is_active`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Contoh data dummy untuk testing
INSERT INTO `instance_mapping` (`hostname`, `instance_id`, `public_ip`, `private_ip`, `security_group_id`, `security_group_name`, `region_id`) VALUES
('iZk1afu5vtecqww9xqgmu1Z', 'i-k1afu5vtecqww9xqgmu1', '147.139.213.142', '10.0.0.1', 'sg-k1a9bjzlyjzcse7it3va', 'SOC-Security-Group', 'ap-southeast-3');

-- Verifikasi tabel dibuat
SHOW TABLES LIKE 'instance_mapping';

-- Lihat struktur tabel
DESCRIBE instance_mapping;

