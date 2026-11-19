# The Movies Dataset (movies_metadata.csv)

H10 defterinin 5. bölümü (açıklama metniyle içerik tabanlı öneri) için. Film açıklamaları (overview) TMDB'den derlenmiştir; MovieLens'in kendi dosyalarında açıklama yoktur.

## İndirme
1. https://www.kaggle.com/datasets/rounakbanik/the-movies-dataset adresine gidin (Kaggle hesabı gerekir).
2. Yalnız `movies_metadata.csv` dosyasını indirin (yaklaşık 34 MB). Bütün arşiv 230 MB; gerekmez.
3. Dosyayı **bu klasöre** koyun: `Veri/movies_metadata/movies_metadata.csv`

MovieLens filmleriyle eşleme `Veri/movielens/ml-latest-small/links.csv` içindeki `tmdbId` sütunu üzerinden yapılır; defter bunu kendisi yapar.

## Bilinen veri kirliliği
- `id` sütununda 3 satırda sayı yerine tarih yazıyor; defter bu satırları atar.
- 45.466 filmden MovieLens'teki 9.737 filmin 9.521'i eşleşir; 216 filmin açıklaması yoktur.

Dosya `.gitignore` sayesinde Git'e girmez; herkes kendisi indirir.
