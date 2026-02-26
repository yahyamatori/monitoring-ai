# Setup Guide - SOC Dashboard IP Block Feature

## Prerequisites
- Python 3.8+
- Django 5.2+
- MySQL Database
- Alibaba Cloud Account (untuk fitur IP Blocking)

---

## Langkah 1: Install Dependencies

### Install Python dependencies:
```
bash
pip install aliyun-python-sdk-core
```

### Install Django (jika belum):
```
bash
pip install django mysqlclient
```

---

## Langkah 2: Setup Database

### Opsi A: Menggunakan Django Migration (Disarankan)

Jalankan perintah ini di direktori project:

```
bash
python manage.py makemigrations dashboard
python manage.py migrate
```

### Opsi B: Manual SQL

Jika lebih suka membuat tabel secara manual, execute file `setup_sql.sql` di MySQL:

```
bash
mysql -u root -p soc < setup_sql.sql
```

Atau copy-paste SQL dari file `setup_sql.sql` ke MySQL client Anda.

---

## Langkah 3: Konfigurasi Alibaba Cloud (Optional)

### Via settings.py

Edit file `soc_dashboard/settings.py` dan isi credentials:

```
python
# Alibaba Cloud Configuration
ALIYUN_ACCESS_KEY = 'LTAI5...'      # Your Access Key ID
ALIYUN_ACCESS_SECRET = '...'          # Your Access Key Secret
ALIYUN_REGION_ID = 'ap-southeast-3'  # Your Region ID
ALIYUN_DEFAULT_SECURITY_GROUP = 'sg-...'  # Your Security Group ID
```

### Cara mendapatkan credentials:
1. Login ke Alibaba Cloud Console
2. Pergi ke IAM (Identity and Access Management)
3. Buat user atau gunakan existing user
4. Buat Access Key untuk user tersebut
5. Catat AccessKeyId dan AccessKeySecret

### Cara mendapatkan Security Group ID:
1. Login ke Alibaba Cloud Console
2. Pergi ke ECS (Elastic Compute Service)
3. Pilih Security Groups
4. Copy Security Group ID yang ingin digunakan

---

## Langkah 4: Restart Service

Restart Django service Anda:

```
bash
# Jika menggunakan systemd
sudo systemctl restart gunicorn

# Jika menggunakan manage.py runserver
# Ctrl+C lalu jalankan lagi: python manage.py runserver
```

---

## Langkah 5: Verifikasi

### Cek apakah tabel sudah dibuat:
```
bash
python manage.py shell
```

Di Django shell:
```
python
from dashboard.models import IpBlock
print(IpBlock.objects.count())
```

### Buka halaman:
- Dashboard: http://domain-anda.com/
- Attack Analysis: http://domain-anda.com/attack-analysis/
- IP Block List: http://domain-anda.com/ip-block/

---

## Troubleshooting

### Error: Table 'soc.ip_block' doesn't exist
- Solution: Jalankan migration atau execute SQL manual

### Error: Alibaba Cloud credentials not configured
- Solution: Isi credentials di settings.py

### Error: aliyun-python-sdk-core not found
- Solution: Install dengan `pip install aliyun-python-sdk-core`

---

## Fitur yang Tersedia

### Attack Analysis (attack-analysis/)
- Filter berdasarkan tanggal, tipe serangan, severity, IP
- Analisis Top Attackers
- Distribusi Attack Types, Severity, Protocol
- Target Ports Analysis
- Attack Patterns
- Tabel detail attack logs

### IP Block List (ip-block/)
- Tambah IP manual
- Auto-add IP berisiko tinggi
- Block IP ke Alibaba Cloud Security Group
- Unblock IP
- Tracking status (pending/blocked/unblocked)

---

## Script Otomatis

Anda bisa menggunakan script `setup_ip_block.sh` untuk setup otomatis:

```
bash
bash setup_ip_block.sh
```

---

## Struktur File

```
.
├── dashboard/
│   ├── models.py          # Model IpBlock
│   └── views.py           # View functions untuk attack analysis & IP blocking
├── soc_dashboard/
│   ├── settings.py        # Konfigurasi Alibaba Cloud
│   └── urls.py            # URL patterns
├── templates/
│   ├── attack_analysis.html   # Template analisis serangan
│   ├── ip_block_list.html      # Template IP block list
│   └── home.html               # Dashboard utama
├── setup_ip_block.sh      # Script setup otomatis
├── setup_sql.sql          # SQL untuk manual setup
└── SETUP_GUIDE.md         # File ini
```

---

## Catatan Keamanan

1. **JANGAN** commit credentials ke git
2. Gunakan environment variables untuk credentials
3. Batasi akses ke halaman admin dan IP block

Contoh menggunakan environment variables:

```
python
import os

ALIYUN_ACCESS_KEY = os.environ.get('ALIYUN_ACCESS_KEY', '')
ALIYUN_ACCESS_SECRET = os.environ.get('ALIYUN_ACCESS_SECRET', '')
ALIYUN_REGION_ID = os.environ.get('ALIYUN_REGION_ID', 'ap-southeast-3')
ALIYUN_DEFAULT_SECURITY_GROUP = os.environ.get('ALIYUN_DEFAULT_SECURITY_GROUP', '')
```

---

## Support

Jika ada pertanyaan, silakan hubungi developer.
