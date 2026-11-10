# MovieLens ml-latest-small

Ara sınav sonrası sınıf içi veri seti. Film puanları (0,5–5 yıldız), film türleri ve kullanıcı etiketleri.

## İndirme
1. https://grouplens.org/datasets/movielens/ adresine gidin, **ml-latest-small.zip** dosyasını indirin
   (doğrudan bağlantı: https://files.grouplens.org/datasets/movielens/ml-latest-small.zip, yaklaşık 1 MB).
2. Zip'i **bu klasöre** (`Veri/movielens/`) açın. Sonuç şöyle olmalı:

```
Veri/movielens/ml-latest-small/
    ratings.csv    100.836 puan (userId, movieId, rating, timestamp)
    movies.csv     9.742 film (movieId, title, genres)
    tags.csv       3.683 etiket
    links.csv      IMDb ve TMDB kimlikleri
    README.txt
```

Dosyalar `.gitignore` sayesinde Git'e girmez.

## Kullanım koşulları (README.txt)
Ticari kullanım yok; yayınlarda atıf: Harper, F. M. ve Konstan, J. A. (2015). The MovieLens Datasets: History and Context. *ACM Transactions on Interactive Intelligent Systems*, 5(4). https://doi.org/10.1145/2827872

## Hangi hafta
H09 ve sonrası (sepet analizi karşılaştırması, içerik tabanlı öneri, işbirlikçi filtreleme, matris çarpanlarına ayırma).
