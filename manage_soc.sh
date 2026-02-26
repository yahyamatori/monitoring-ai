#!/bin/bash

case $1 in
    start)
        echo "🚀 Memulai SOC Django..."
        sudo systemctl start soc-django.service
        sudo systemctl status soc-django.service
        ;;
    stop)
        echo "🛑 Menghentikan SOC Django..."
        sudo systemctl stop soc-django.service
        sudo systemctl status soc-django.service
        ;;
    restart)
        echo "🔄 Merestart SOC Django..."
        sudo systemctl restart soc-django.service
        sudo systemctl status soc-django.service
        ;;
    status)
        echo "📊 Status SOC Django:"
        sudo systemctl status soc-django.service
        ;;
    log)
        echo "📝 Log SOC Django (tekan Ctrl+C untuk keluar):"
        sudo journalctl -u soc-django.service -f
        ;;
    enable)
        echo "🔌 Mengaktifkan auto-start..."
        sudo systemctl enable soc-django.service
        echo "✅ Auto-start diaktifkan"
        ;;
    disable)
        echo "🔌 Menonaktifkan auto-start..."
        sudo systemctl disable soc-django.service
        echo "✅ Auto-start dinonaktifkan"
        ;;
    *)
        echo "❌ Perintah tidak dikenal"
        echo "Penggunaan: ./manage_soc.sh [start|stop|restart|status|log|enable|disable]"
        ;;
esac
