#  AnimeFansub-Dizi-Film Platformu

Humat Fansub, anime tutkunları için basit ama gerekli özellikleri barındıran bir fansub platformudur. Kullanıcılar, anime serilerini izleyebilir ve bölümler arasında gezinebilirler. Platformda yer alan admin paneli ile yöneticiler yeni anime serileri ve bölümleri ekleyebilir, platformu kolayca yönetebilir.

> **Not:** Bu projeyi hayata geçirmeden önce **secret key** değerini değiştirmeyi ve veritabanını yeniden oluşturmayı unutmayın(veritabanı.txt, dosyasından kkopya çekebilirsiniz). Kodları inceleyerek güvenlik önlemlerini almanız önerilir.

## Özellikler

- **Anime Seçimi:** Kullanıcılar, mevcut anime serilerini seçip izleyebilirler.
- **Bölüm Seçimi:** Her anime serisi için uygun bölümler listelenir ve kullanıcılar istedikleri bölümü izleyebilirler.
- **Video Embed:** Videolar, iframe ile dış kaynaklardan platforma eklenmiştir.
- **Admin Panel:** Yöneticiler anime serileri ve bölümlerini ekleyebilir, silebilir, düzenleyebilir.


3. **Admin Girişi:**
   - Kullanıcı Adı: `admin`
   - Şifre: `adminpsw`

## Canlı Demo

> **Dikkat:** Vercel üzerinde barındırılan örnekte herhangi bir veritabanı işlemi yapamazsınız. Vercel, sunucu taraflı veritabanı işlemlerine izin vermemektedir.

> **Dikkat:** Çalışan Hümat Fansuba air versyon:
[www.humatfansub.com.tr](https://www.humatfansub.com.tr)


## Güvenlik

Projeyi kullanmadan önce mutlaka güvenlik önlemlerini gözden geçirin. Secret key'i güncelleyip güçlü bir şifre kullanmayı unutmayın. Admin paneli ve veritabanı işlemleri için ek güvenlik katmanları ekleyebilirsiniz.

## Lisans

Bu proje MIT Lisansı altında lisanslanmıştır. Daha fazla bilgi için `LICENSE` dosyasına göz atın.



## Açık Kaynak Felsefesi

Bu proje, açık kaynak topluluğunun gücüne inanılarak geliştirilmiştir. Herkesin katkıda bulunabileceği ve kodun şeffaf bir şekilde paylaşılmasının yazılım dünyasına önemli bir katkı sağladığına inanıyoruz. Eğer bu projeye katkıda bulunmak istiyorsanız, önerilerinizi ve geliştirmelerinizi paylaşabilirsiniz.

Projeyi geliştirirken karşılaştığınız sorunları çözebilir, yeni özellikler ekleyebilir veya mevcut olanları iyileştirebilirsiniz. Ayrıca, topluluğa yardımcı olmak amacıyla belgeleri geliştirerek veya çeviriler yaparak katkıda bulunabilirsiniz.

### Katkıda Bulunma Adımları

1. Bu depoyu fork'layın.
2. Yeni bir özellik eklemek için bir branch oluşturun: `git checkout -b yeni-ozellik`
3. Yaptığınız değişiklikleri commitleyin: `git commit -m 'Yeni özellik eklendi'`
4. Branch'inizi push edin: `git push origin yeni-ozellik`
5. Bir Pull Request oluşturun.
