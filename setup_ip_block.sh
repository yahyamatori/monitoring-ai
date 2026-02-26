#!/bin/bash
# Script Setup IP Block untuk SOC Dashboard
# Jalankan dengan: bash setup_ip_block.sh

echo "========================================="
echo "Setup IP Block untuk SOC Dashboard"
echo "========================================="

# 1. Install dependencies untuk Alibaba Cloud SDK
echo ""
echo "[1/4] Menginstall dependencies..."
pip install aliyun-python-sdk-core

# 2. Generate Django migration
echo ""
echo "[2/4] Generate migration..."
python manage.py makemigrations dashboard

# 3. Apply migration
echo ""
echo "[3/4] Apply migration ke database..."
python manage.py migrate

# 4. Restart Django service
echo ""
echo "[4/4] Restart Django service..."
# Untuk systemd
sudo systemctl restart gunicorn  # atau service yang Anda gunakan
# ATAU jika menggunakan manage.py runserver
# sudo systemctl restart django

echo ""
echo "========================================="
echo "Setup Selesai!"
echo "========================================="
echo ""
echo "Langkah selanjutnya:"
echo "1. Konfigurasi credentials Alibaba Cloud di settings.py"
echo "2. Buka halaman IP Block List di /ip-block/"
echo ""
