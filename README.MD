# SmartTravel - Proje Kurulum Kılavuzu

Hocam projeyi kendi bilgisayarınızda sıfır hata ile çalıştırmak için lütfen sırasıyla şu adımları takip edin:

1. **Gerekli Kütüphaneleri Kurun:**
   ```bash
   pip install -r requirements.txt

Veritabanı Ayarı:

PostgreSQL sunucunuzda smarttravel adında boş bir veritabanı oluşturun.

Türkçe karakter uyumluluğu için veritabanında şu sorguyu çalıştırın:
CREATE EXTENSION IF NOT EXISTS unaccent;

settings.py dosyasındaki DATABASES ayarına yerel PostgreSQL şifrenizi yazın.

3.Tabloları Oluşturun (Migration):
python manage.py migrate

4.Hazır Otel ve Oda Verilerini Yükleyin:
python manage.py loaddata veriler.json

Projeyi Başlatın:
python manage.py runserver