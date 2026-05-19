# SmartTravel - Proje Kurulum Kılavuzu

Hocam projeyi kendi bilgisayarınızda sıfır hata ile çalıştırmak için lütfen sırasıyla şu adımları takip edin:

1. **Gerekli Kütüphaneleri Kurun:**
   ```bash
   pip install -r requirements.txt

Veritabanı Ayarı:

PostgreSQL sunucunuzda smarttravel adında boş bir veritabanı oluşturun.
ardından settings.py klasöründeki databases kısmına postgresql şifrenizi giriniz

Türkçe karakter uyumluluğu için veritabanında şu sorguyu çalıştırın:
CREATE EXTENSION IF NOT EXISTS unaccent;

Yapay Zeka (Gemini AI) Ayarı

Projedeki chatbot özelliğinin çalışabilmesi için Gemini API anahtarınızı terminale tanımlamanız gerekmektedir. Projeyi çalıştırmadan önce terminalinizde şu komutu çalıştırın:

* **Windows (CMD) için:** `set GEMINI_API_KEY=kendi_api_anahtarınız`
* **Windows (PowerShell) için:** `$env:GEMINI_API_KEY="kendi_api_anahtarınız"`
* **Mac/Linux için:** `export GEMINI_API_KEY="kendi_api_anahtarınız"`

settings.py dosyasındaki DATABASES ayarına yerel PostgreSQL şifrenizi yazın.

3.Tabloları Oluşturun (Migration):
python manage.py migrate

4.Hazır Otel ve Oda Verilerini Yükleyin:
python manage.py loaddata veriler.json

Projeyi Başlatın:
python manage.py runserver