-- =====================================================
-- SQL Migration untuk menambahkan kolom yang hilang di tabel ip_block
-- SOC Dashboard
-- =====================================================

-- Tambahkan kolom hostname jika belum ada
ALTER TABLE ip_block ADD COLUMN hostname VARCHAR(255) NULL AFTER severity;

-- Tambahkan kolom instance_id jika belum ada  
ALTER TABLE ip_block ADD COLUMN instance_id VARCHAR(50) NULL AFTER hostname;

-- Verifikasi struktur tabel setelah perubahan
