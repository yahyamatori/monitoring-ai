# TODO - Attack Analysis Menu

## Plan:
- [x] 1. Tambahkan fungsi view `attack_analysis` di `dashboard/views.py`
- [x] 2. Tambahkan URL pattern di `soc_dashboard/urls.py`
- [x] 3. Buat template baru `templates/attack_analysis.html` (sudah ada)
- [x] 4. Update `templates/home.html` - tambahkan menu link
- [x] 5. Buat template `templates/ip_block_list.html` untuk IP blocking
- [x] 6. Update `templates/attack_analysis.html` - tambahkan menu link IP Block
- [x] 7. Update `soc_dashboard/settings.py` - tambahkan konfigurasi Alibaba Cloud

## Completed Features:
- Attack Analysis menu dengan filter (date range, attack type, severity, IP)
- Analisis pola serangan: top attackers, attack types, severity, protocol, ports
- IP Block List untuk memblokir IP attacker via Alibaba Cloud Security Group
- Menu sidebar yang menghubungkan ke kedua halaman
