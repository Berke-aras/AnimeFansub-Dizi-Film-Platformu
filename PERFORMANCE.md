# Anime Fansub Platform - Performance Optimizasyonları

Bu proje, düşük kaynaklı sunucularda da hızlı çalışacak şekilde optimize edilmiştir.

## Yapılan Optimizasyonlar

### 1. Database Optimizasyonları

-   **İndeksler**: Sık kullanılan alanlara database indeksleri eklendi
-   **Lazy Loading**: İlişkili verilerin sadece gerektiğinde yüklenmesi
-   **Query Optimizasyonu**: JOIN kullanımı ve gereksiz sorguların azaltılması
-   **SQLite Optimizasyonu**: WAL mode, cache ayarları ve pragma optimizasyonları

### 2. Caching Sistemi

-   **Simple Cache**: Hafif, dependency gerektirmeyen basit cache sistemi
-   **Route Caching**: Ana sayfalar için cache mekanizması
-   **Function Caching**: Ağır işlemler için fonksiyon seviyesinde cache

### 3. Memory Optimizasyonu

-   **Lazy Loading**: ORM ilişkilerinde lazy loading kullanımı
-   **Pagination**: Büyük veri setlerinde sayfalama ile memory kullanımının azaltılması
-   **Session Optimizasyonu**: Session yaşam süresinin kısaltılması

### 4. Performance Monitoring

-   **Yavaş Sorgu Takibi**: 1 saniyeden uzun süren isteklerin loglanması
-   **Response Time Headers**: Debug için response time bilgisi
-   **Function Timing**: Yavaş fonksiyonların takibi

## Deployment İçin Öneriler

### 1. Production Sunucu Kurulumu

```bash
# Dependencies yükle
pip install gunicorn

# Production script'ini çalıştır
chmod +x deploy_production.sh
./deploy_production.sh

# Gunicorn ile başlat
gunicorn -c gunicorn.conf.py wsgi:application
```

### 2. Nginx Reverse Proxy

-   Static dosyalar için nginx kullanımı
-   Gzip sıkıştırma
-   SSL/TLS terminasyonu
-   Load balancing (gerekirse)

### 3. Database Optimizasyonu

```bash
# Database optimizasyonunu çalıştır
python optimize_database.py

# İndeksleri oluştur
python create_indexes_migration.py
```

### 4. Monitoring

-   Performance loglarını izleyin: `tail -f performance.log`
-   System resource kullanımını takip edin
-   Database query sürelerini kontrol edin

## Performans Metrikleri

### Hedef Performans (Düşük Kaynak Sunucu)

-   **Ana Sayfa**: < 500ms
-   **Anime Listesi**: < 1s (18 item per page)
-   **Episode Sayfası**: < 300ms
-   **Search**: < 800ms

### Resource Kullanımı

-   **RAM**: < 512MB (cache dahil)
-   **CPU**: < 50% (normal kullanımda)
-   **Disk I/O**: Optimize edilmiş SQLite queries

## Monitoring ve Debugging

### Log Dosyaları

-   `performance.log`: Yavaş request ve function logları
-   `logs/access.log`: Gunicorn access logları
-   `logs/error.log`: Application error logları

### Performance İzleme

```bash
# Gerçek zamanlı performans izleme
tail -f performance.log | grep "SLOW"

# System resource izleme
htop
iotop
```

### Database Analizi

```sql
-- Yavaş query'leri bul
.timer on
EXPLAIN QUERY PLAN SELECT * FROM anime WHERE name LIKE '%search%';

-- Database istatistikleri
.stats on
```

## Production Checklist

-   [ ] Debug mode kapatıldı
-   [ ] Database optimize edildi
-   [ ] İndeksler oluşturuldu
-   [ ] Gunicorn/uWSGI kuruldu
-   [ ] Nginx yapılandırıldı
-   [ ] SSL sertifikası kuruldu
-   [ ] Log rotation ayarlandı
-   [ ] Backup sistemi kuruldu
-   [ ] Monitoring sistemi aktif
-   [ ] Error tracking aktif

## Performans Tuning Tavsiyeleri

### Düşük Kaynak Sunucu (1-2GB RAM)

```python
# gunicorn.conf.py ayarları
workers = 2
worker_connections = 500
max_requests = 500
```

### Orta Kaynak Sunucu (4-8GB RAM)

```python
# gunicorn.conf.py ayarları
workers = 4
worker_connections = 1000
max_requests = 1000
```

### Database Cache Ayarları

```sql
-- SQLite cache boyutu (MB cinsinden)
PRAGMA cache_size = -64000;  -- 64MB
```

## Troubleshooting

### Yavaş Performance

1. Performance loglarını kontrol edin
2. Database query'lerini optimize edin
3. Cache hit ratio'yu kontrol edin
4. System resource kullanımını izleyin

### Memory Leaks

1. Gunicorn worker restart ayarlarını kontrol edin
2. Database connection pool'ları kontrol edin
3. Cache boyutunu kontrol edin

### High CPU Usage

1. Worker sayısını azaltın
2. Database indekslerini kontrol edin
3. Inefficient query'leri bulun ve optimize edin
