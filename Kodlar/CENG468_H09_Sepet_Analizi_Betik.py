"""
CENG468 Veri Madenciliği · Hafta 9
Sepet analizi, uçtan uca betik: veriden rapora

Öğr. Gör. Dr. Duygu TOPALOĞLU · 2026-2027 Güz

Bu dosya H06 defterinin (CENG468_H06_Sepet_Analizi.ipynb) tek parça hâlidir.
Defterde hücre hücre, tahmin ederek ilerledik. Burada aynı iş baştan sona
tek seferde çalışır ve sonunda bir RAPOR üretir. Amaç: bir analiz betiğinin
nasıl kurulduğunu ve çıktısının nasıl okunduğunu görmek.

İki çalıştırma biçimi:
  (a) Betik olarak, baştan sona (terminal), aşağıdaki komutlarla.
  (b) Hücre hücre: VS Code'da dosyayı açın, her "# %%" satırı bir hücredir;
      Shift+Enter ile sırayla çalıştırın (Jupyter uzantısı, "Interactive Window").
      Bu modda komut satırı argümanı yoktur: [0] AYARLAR hücresinde
      VERI_SETI ve ALT_KUME değişkenleri varsayılanla (MovieLens) başlar, istediğinizi elle yazın.
      Aynı dosya, iki görünüm: ara değişkenleri incelemek için (b), sonucu almak için (a).

Çalıştırma (repo kökünde, uv ortamı etkinken):
    uv run python Kodlar/CENG468_H09_Sepet_Analizi_Betik.py                 # MovieLens (varsayılan)
    uv run python Kodlar/CENG468_H09_Sepet_Analizi_Betik.py online_retail   # Online Retail II (Almanya)
    uv run python Kodlar/CENG468_H09_Sepet_Analizi_Betik.py online_retail all   # bütün ülkeler

Aynı algoritma iki farklı veriye uygulanır. Kod değişmez, sepetin tanımı değişir:
    Online Retail II : sepet = fatura,     öğe = ürün (aynı faturadaki ürünler)
    MovieLens        : sepet = kullanıcı,  öğe = film  (aynı kullanıcının 4+ puan verdiği filmler)

Adımlar:
    1. Veriyi yükle ve temizle            (H03, H05)
    2. Satırdan sepete: sepet × öğe tablosu (H06 Bölüm 1)
    3. Destek, güven, kaldıraç: elle       (H06 Bölüm 2–3)
    4. Apriori ile sık kümeler, kurallar   (H06 Bölüm 5)
    5. Kuraldan öneriye                    (H06 Bölüm 6)
    6. Rapor: sayıları cümleye çevir       (yeni)
"""

import math
import os
import sys
import time

import pandas as pd
from mlxtend.frequent_patterns import apriori, association_rules

pd.set_option("display.width", 140)
pd.set_option("display.max_columns", 12)
pd.set_option("display.max_colwidth", 45)


# %% [0] AYARLAR
# ----------------------------------------------------------------------------
# Komut satırından veri seti adı gelmezse MovieLens kullanılır.
# Terminalde: argümanlar okunur. VS Code Interactive Window / Jupyter çekirdeğinde
# sys.argv = ['ipykernel_launcher.py', '-f', '<bağlantı>.json'] olduğundan okunmaz;
# orada aşağıdaki iki değişkeni elle değiştirin (ör. VERI_SETI = "online_retail").
_ARGS = [] if "ipykernel" in sys.modules else sys.argv[1:]
VERI_SETI = _ARGS[0] if len(_ARGS) > 0 else "movielens"
ALT_KUME = _ARGS[1] if len(_ARGS) > 1 else None   # ör. "Germany", "all"

AYARLAR = {
    "online_retail": {
        "baslik": "Online Retail II (UCI), 2010-2011",
        "sepet_adi": "fatura",
        "oge_adi": "ürün",
        "alt_kume": "Germany" if ALT_KUME is None else ALT_KUME,  # H06'daki gibi tek ülke
        "min_support": 0.05 if ALT_KUME != "all" else 0.02,   # H06 Bölüm 5 (tek ülke) ve E3 (bütün veri)
        "min_lift": 1.0,
        "max_len": None,           # küme uzunluğu sınırı yok (sepetler küçük)
        "en_az_birlikte": 50,      # elle incelemede güvenilir saymak için en az kaç sepet
    },
    "movielens": {
        "baslik": "MovieLens ml-latest-small (GroupLens)",
        "sepet_adi": "kullanıcı",
        "oge_adi": "film",
        "alt_kume": None,
        "begeni_esigi": 4.0,       # 4 ve üzeri puan = "beğendi" = sepette var
        "min_support": 0.10,       # 610 kullanıcının en az %10'u = 61 kullanıcı
        "min_lift": 1.0,
        "max_len": 2,              # sepetler büyük (onlarca film); ikili kurallarla sınırla
        "en_az_birlikte": 30,
    },
}
if VERI_SETI not in AYARLAR:
    sys.exit(f"Bilinmeyen veri seti: {VERI_SETI}. Seçenekler: {list(AYARLAR)}")
A = AYARLAR[VERI_SETI]

# Çıktı klasörü: her çalıştırma kendi raporunu yazar
# (alt küme adı klasöre girer: Almanya ve "all" birbirinin raporunu silmesin)
CIKTI = os.path.join("Ciktilar", f"sepet_{VERI_SETI}"
                     + (f"_{A['alt_kume'].lower()}" if A.get("alt_kume") else ""))
os.makedirs(CIKTI, exist_ok=True)


def baslik(no, metin):
    """Her adımın başında ekrana bir başlık basar."""
    print("\n" + "=" * 78)
    print(f"ADIM {no}: {metin}")
    print("=" * 78)


t0 = time.time()
print(f"Veri seti: {A['baslik']}")
print(f"Sepet = {A['sepet_adi']}, öğe = {A['oge_adi']}")


# %% [1] VERİYİ YÜKLE VE TEMİZLE (H03, H05, H06 Bölüm 0)
# ----------------------------------------------------------------------------
# Bu adımın çıktısı her iki veri için aynı biçimdedir:
#   uzun  : DataFrame, her satır bir (sepet, oge) çifti
#   isimler: öğe kodundan ada eşleme (raporda ad göstermek için)
baslik(1, "Veriyi yükle ve temizle")

if VERI_SETI == "online_retail":
    VERI = os.path.join("Veri", "online_retail")
    XLSX = os.path.join(VERI, "online_retail_II.xlsx")
    CSV = os.path.join(VERI, "online_retail_2010_2011.csv")

    if os.path.exists(CSV):
        df = pd.read_csv(CSV, dtype={"Invoice": str, "StockCode": str},
                         parse_dates=["InvoiceDate"])
    elif os.path.exists(XLSX):
        df = pd.read_excel(XLSX, sheet_name="Year 2010-2011",
                           dtype={"Invoice": str, "StockCode": str})
        df.to_csv(CSV, index=False)
    else:
        sys.exit("Veri dosyası bulunamadı: " + os.path.abspath(XLSX)
                 + "\nVeri/online_retail/BENIOKU.md dosyasındaki adımları izle.")
    print(f"Ham veri: {len(df):,} satır")

    # H06 Bölüm 0'daki temizlik kararları, aynı sırayla (her adım kaç satır sildi?)
    d = df
    for kural, aciklama in [
        (lambda v: ~v["Invoice"].str.startswith("C"),   "İptal faturalar ('C')"),        # satış değil, iptal
        (lambda v: ~v["Invoice"].str.startswith("A"),   "Düzeltme faturaları ('A')"),    # muhasebe düzeltmesi
        (lambda v: v["Quantity"] > 0,                   "Adet sıfır ya da eksi"),        # stok düzeltmeleri
        (lambda v: v["Price"] > 0,                      "Fiyat sıfır ya da eksi"),       # para el değiştirmemiş
        (lambda v: v["StockCode"].str[0].str.isdigit(), "Ürün dışı kodlar"),             # kargo (POSTAGE), komisyon, indirim
        (lambda v: ~v.duplicated(),                     "Tekrarlı satırlar"),            # kayıt tekrarı
    ]:
        once = len(d)
        d = d[kural(d)]
        print(f"  {aciklama:<28} -{once - len(d):>7,} satır → {len(d):,}")
    df_temiz = d

    # Ülke alt kümesi (H06'da Almanya ile çalıştık; "all" bütün ülkeler)
    if A["alt_kume"] and A["alt_kume"] != "all":
        df_temiz = df_temiz[df_temiz["Country"] == A["alt_kume"]]
        print(f"  Yalnız {A['alt_kume']}: {len(df_temiz):,} satır")

    # YENİ (H06'da yoktu): H06 Bölüm 6'da "ileride temizleyeceğiz" dediğimiz ad sonu boşlukları.
    # ("ROUND SNACK BOXES SET OF 4 FRUITS " ile "...FRUITS" aynı ürün olsun)
    df_temiz = df_temiz.assign(Description=df_temiz["Description"].str.strip())

    uzun = df_temiz[["Invoice", "Description"]].rename(
        columns={"Invoice": "sepet", "Description": "oge"})
    isimler = None   # ürün adı zaten öğe

elif VERI_SETI == "movielens":
    VERI = os.path.join("Veri", "movielens", "ml-latest-small")
    # Zip bir kat fazla açılmışsa (ml-latest-small/ml-latest-small/ratings.csv) onu da kabul et
    if not os.path.exists(os.path.join(VERI, "ratings.csv")) and \
            os.path.exists(os.path.join(VERI, "ml-latest-small", "ratings.csv")):
        VERI = os.path.join(VERI, "ml-latest-small")
    RATINGS = os.path.join(VERI, "ratings.csv")
    MOVIES = os.path.join(VERI, "movies.csv")
    if not os.path.exists(RATINGS):
        sys.exit("Veri dosyası bulunamadı: " + os.path.abspath(RATINGS)
                 + "\nVeri/movielens/BENIOKU.md dosyasındaki adımları izle.")
    ratings = pd.read_csv(RATINGS)
    movies = pd.read_csv(MOVIES)
    print(f"Ham veri: {len(ratings):,} puan · {ratings['userId'].nunique():,} kullanıcı · "
          f"{ratings['movieId'].nunique():,} film")

    # Temizlik kararı: "sepette var" = kullanıcı filmi BEĞENDİ (puan >= eşik).
    # Düşük puan verilen film sepete girmez; aksi hâlde "izledi ama sevmedi"
    # filmler de "birlikte alındı" sayılır. Bu bir KARAR; eşiği değiştirip bak.
    once = len(ratings)
    ratings = ratings[ratings["rating"] >= A["begeni_esigi"]]
    print(f"  Puan < {A['begeni_esigi']} olan satırlar     -{once - len(ratings):>7,} → {len(ratings):,}")

    uzun = ratings[["userId", "movieId"]].rename(columns={"userId": "sepet", "movieId": "oge"})
    isimler = movies.set_index("movieId")["title"]

print(f"Uzun tablo: {len(uzun):,} (sepet, öğe) çifti · "
      f"{uzun['sepet'].nunique():,} {A['sepet_adi']} · {uzun['oge'].nunique():,} {A['oge_adi']}")


# %% [2] SATIRDAN SEPETE: SEPET × ÖĞE TABLOSU (H06 Bölüm 1)
# ----------------------------------------------------------------------------
baslik(2, "Satırdan sepete: sepet × öğe tablosu")

# H06 Bölüm 1'deki üç adım tek satırda: groupby + size → unstack → > 0
# size(): her (sepet, öğe) çifti kaç kez geçti; > 0: "var mı?" sorusuna çevirir.
def ad(oge):
    """Öğe kodunu rapor için okunur ada çevirir."""
    return str(isimler.get(oge, oge)) if isimler is not None else str(oge)

sepet = uzun.groupby(["sepet", "oge"]).size().unstack(fill_value=0) > 0

n_sepet, n_oge = sepet.shape
doluluk = sepet.values.mean() * 100
print(f"Sepet tablosu: {n_sepet:,} satır ({A['sepet_adi']}) × {n_oge:,} sütun ({A['oge_adi']})")
print(f"Dolu hücre oranı: %{doluluk:.2f}  → tablo seyrek (sparse)")
sepet_boyu = sepet.sum(axis=1)
print(f"Sepet büyüklüğü: ortalama {sepet_boyu.mean():.1f}, medyan {sepet_boyu.median():.0f}, "
      f"en büyük {sepet_boyu.max()}")
en_sik5 = sepet.sum().nlargest(5).index
dolu5 = sepet[en_sik5].sum(axis=1).nlargest(5).index      # bu 5 öğeden en çoğunu içeren 5 sepet
print("\nEn sık 5 öğe × onlardan en çoğunu içeren 5 sepet (1 = var):")
print(sepet.loc[dolu5, en_sik5].astype(int).rename(columns=lambda c: ad(c)[:28]))


# %% [3] DESTEK, GÜVEN, KALDIRAÇ: ELLE (H06 Bölüm 2–3)
# ----------------------------------------------------------------------------
baslik(3, "Destek, güven, kaldıraç: elle (tek kural)")

def destek(tablo, a):
    """Support(A): A'nın geçtiği sepetlerin oranı."""
    return tablo[a].mean()

def guven(tablo, a, b):
    """Confidence(A → B): A'lı sepetlerin ne kadarında B de var?"""
    return (tablo[a] & tablo[b]).mean() / tablo[a].mean()

def kaldirac(tablo, a, b):
    """Lift(A → B): A, B'yi görme olasılığını kaç kat değiştiriyor?"""
    return guven(tablo, a, b) / tablo[b].mean()

# Örnek kural: en sık öğe (A) ve onunla en az N sepette birlikte geçen,
# kaldıracı en yüksek öğe (B). Her veri setinde kendiliğinden seçilir.
A_oge = sepet.sum().idxmax()
birlikte = sepet.loc[sepet[A_oge]].sum().drop(A_oge)          # A'lı sepetlerde her öğe kaç kez
adaylar = birlikte[birlikte >= A["en_az_birlikte"]].index
B_oge = max(adaylar, key=lambda b: kaldirac(sepet, A_oge, b))

print(f"A = {ad(A_oge)}")
print(f"B = {ad(B_oge)}   (A ile en az {A['en_az_birlikte']} sepette birlikte geçenler arasında kaldıracı en yüksek)")
print(f"  Support(A)        = {destek(sepet, A_oge):.4f}  → bütün sepetlerde A görülme oranı %{destek(sepet, A_oge)*100:.1f}")
print(f"  Support(B)        = {destek(sepet, B_oge):.4f}  → bütün sepetlerde B görülme oranı %{destek(sepet, B_oge)*100:.1f}")
print(f"  Support(A, B)     = {(sepet[A_oge] & sepet[B_oge]).mean():.4f}  → birlikte {int((sepet[A_oge] & sepet[B_oge]).sum()):,} sepet")
print(f"  Confidence(A → B) = {guven(sepet, A_oge, B_oge):.4f}  → A'lı sepetlerde B görülme oranı %{guven(sepet, A_oge, B_oge)*100:.1f}")
print(f"  Lift(A → B)       = {kaldirac(sepet, A_oge, B_oge):.2f}    → A, B'yi görme olasılığını {kaldirac(sepet, A_oge, B_oge):.2f} kat artırıyor")
print(f"  Confidence(B → A) = {guven(sepet, B_oge, A_oge):.4f}  → güven yöne bağlı")
print(f"  Lift(B → A)       = {kaldirac(sepet, B_oge, A_oge):.2f}    → kaldıraç simetrik")

# Kaldıraç tuzağı (H06 "iz sür"): A ile birlikte geçen BÜTÜN öğeler arasında
# kaldıracı en yüksek 5'i. Kaç sepete dayandıklarına bak.
tuzak_tablo = pd.DataFrame({
    "oge": [ad(b) for b in birlikte.index],
    "birlikte_sepet": birlikte.values,
    "kaldirac": [kaldirac(sepet, A_oge, b) for b in birlikte.index],
}).query("birlikte_sepet > 0").nlargest(5, "kaldirac")
print(f"\nKaldıraç tuzağı: {ad(A_oge)} ile kaldıracı en yüksek 5 öğe (destek eşiği YOK):")
print(tuzak_tablo.to_string(index=False))
print("→ Üstteki kaldıraçlar yüksek ama kaç sepete dayanıyor? Apriori'de destek eşiği bunun için var.")
print(f"→ Kaldıracın üst sınırı 1 / Support(A) = {1 / destek(sepet, A_oge):.2f}: B yalnız A'lı sepetlerde geçiyorsa bu sınıra dayanır.")


# %% [4] APRIORI İLE SIK KÜMELER VE KURALLAR (H06 Bölüm 4–5)
# ----------------------------------------------------------------------------
baslik(4, f"Apriori: sık kümeler (min_support = {A['min_support']}) ve kurallar (lift ≥ {A['min_lift']})")

t1 = time.time()
kumeler = apriori(sepet, min_support=A["min_support"], use_colnames=True, max_len=A["max_len"])
kumeler["uzunluk"] = kumeler["itemsets"].apply(len)
print(f"Sık küme sayısı: {len(kumeler):,}  (süre {time.time() - t1:.1f} sn)")
print("Uzunluğa göre:", kumeler["uzunluk"].value_counts().sort_index().to_dict())

if len(kumeler[kumeler["uzunluk"] >= 2]) == 0:
    sys.exit("Hiç ikili sık küme yok: min_support çok yüksek. AYARLAR'dan düşürüp yeniden çalıştır.")

kurallar = association_rules(kumeler, metric="lift", min_threshold=A["min_lift"])
kurallar["sepet_sayisi"] = (kurallar["support"] * n_sepet).round().astype(int)
kurallar["A"] = kurallar["antecedents"].apply(lambda s: ", ".join(ad(x) for x in s))
kurallar["B"] = kurallar["consequents"].apply(lambda s: ", ".join(ad(x) for x in s))
kurallar = kurallar.sort_values("lift", ascending=False).reset_index(drop=True)
print(f"Kural sayısı: {len(kurallar):,}")
print("\nKaldıracı en yüksek 10 kural:")
print(kurallar[["A", "B", "support", "confidence", "lift", "sepet_sayisi"]].head(10).to_string())

kurallar[["A", "B", "support", "confidence", "lift", "sepet_sayisi"]].to_csv(
    os.path.join(CIKTI, "kurallar.csv"), index=False)


# %% [5] KURALDAN ÖNERİYE (H06 Bölüm 6)
# ----------------------------------------------------------------------------
baslik(5, "Kuraldan öneriye: bir sepete ne önerelim?")

def sepete_oner(kurallar, sepet_kumesi, n=5):
    """Öncülü (antecedents) sepetin alt kümesi olan kuralların sonuçlarını,
    kaldıraca göre sıralı önerir. Sepette zaten olan öğeler önerilmez."""
    uygun = kurallar[kurallar["antecedents"].apply(lambda a: a <= sepet_kumesi)]
    oneriler = {}
    for _, satir in uygun.iterrows():
        for oge in satir["consequents"]:
            if oge not in sepet_kumesi:
                oneriler[oge] = max(oneriler.get(oge, 0), satir["lift"])
    return pd.Series(oneriler, dtype=float).sort_values(ascending=False).head(n)

# Örnek sepet: en sık öğeyi (A) alan müşteri
ornek_sepet = {A_oge}
oneri = sepete_oner(kurallar, ornek_sepet)
print(f"Sepette: {ad(A_oge)}")
if len(oneri):
    print("Öneriler (kaldıraç):")
    for oge, l in oneri.items():
        print(f"  {ad(oge):<50} {l:5.2f}")
else:
    print("  Bu öğe için kural yok → soğuk başlangıç: en çok satanlara dön (H05).")


# %% [6] RAPOR: SAYILARI CÜMLEYE ÇEVİR (yeni)
# ----------------------------------------------------------------------------
# Öğrencinin kendi raporunda kurması gereken yapı bu. Sayılar koddan gelir,
# cümle şablonu aynı kalır. Rapor hem ekrana basılır hem dosyaya yazılır.
baslik(6, "Rapor")

def kural_cumlesi(k):
    """Bir kural satırını üç cümlelik okunur yoruma çevirir."""
    return (f"**{k['A']} → {k['B']}.** "
            f"{k['A']} içeren sepetlerde {k['B']} görülme oranı %{k['confidence']*100:.0f} (güven {k['confidence']:.2f}). "
            f"Bütün sepetlerde {k['B']} görülme oranı %{k['consequent support']*100:.1f}; "
            f"yani {k['A']} bu olasılığı {k['lift']:.2f} kat artırıyor (kaldıraç). "
            f"Kural {k['sepet_sayisi']:,} sepete dayanıyor (destek %{k['support']*100:.1f}).")

# İlk 5: aynı öğe çiftinin iki yönü (A→B, B→A) aynı kaldıraca sahip; raporda her çifti bir kez say
gorulen, secilen = set(), []
for _, k in kurallar.iterrows():
    cift = frozenset(k["antecedents"] | k["consequents"])
    if cift not in gorulen:
        gorulen.add(cift)
        secilen.append(k)
    if len(secilen) == 5:
        break
ilk5 = pd.DataFrame(secilen)
en_guvenilir = kurallar.sort_values("confidence", ascending=False).iloc[0]
en_sik = kurallar.sort_values("support", ascending=False).iloc[0]
tuzak = tuzak_tablo.iloc[0]   # Adım 3'teki destek eşiksiz en yüksek kaldıraç

R = []
R.append(f"# Sepet analizi raporu: {A['baslik']}")
R.append("")
R.append("## 1. Veri ve kurulum")
R.append(f"- Sepet tanımı: {A['sepet_adi']}; öğe: {A['oge_adi']}"
         + (f"; alt küme: {A['alt_kume']}" if A.get("alt_kume") else "")
         + (f"; beğeni eşiği: puan ≥ {A['begeni_esigi']}" if "begeni_esigi" in A else ""))
R.append(f"- {n_sepet:,} sepet × {n_oge:,} öğe; dolu hücre oranı %{doluluk:.2f}; "
         f"sepet büyüklüğü ortalama {sepet_boyu.mean():.1f}, medyan {sepet_boyu.median():.0f}")
R.append(f"- Eşikler: min_support = {A['min_support']} (en az {math.ceil(A['min_support']*n_sepet)} sepet), "
         f"lift ≥ {A['min_lift']}" + (f", en çok {A['max_len']} öğeli kümeler" if A["max_len"] else ""))
R.append(f"- Sonuç: {len(kumeler):,} sık küme, {len(kurallar):,} kural")
R.append("")
R.append("## 2. Öne çıkan kurallar (kaldıraca göre ilk 5)")
for i, (_, k) in enumerate(ilk5.iterrows(), 1):
    R.append(f"{i}. " + kural_cumlesi(k))
R.append("")
R.append("## 3. Ölçüler nasıl okunur")
R.append("| Ölçü | Hangi soruyu cevaplar | Yüksekse | Düşükse | Tuzak |")
R.append("|---|---|---|---|---|")
R.append("| Destek (support) | Kural kaç sepete dayanıyor? | Yaygın, güvenilir | Az sepet, tesadüf olabilir | Yüksek destek sıkıcı kural da olabilir (herkes alıyor) |")
R.append("| Güven (confidence) | A alan, B'yi ne sıklıkla alıyor? | A'dan B'ye güçlü geçiş | Zayıf geçiş | Popüler B her kuralda yüksek güven verir |")
R.append("| Kaldıraç (lift) | A, B'yi görme olasılığını kaç kat değiştiriyor? | A ve B birbirini çekiyor | ≈1 bağımsız, <1 birbirini itiyor | Seyrek öğelerde şişer; desteğe birlikte bak |")
R.append("")
R.append("## 4. Karşılaştırma: aynı veri, farklı ölçüler")
R.append(f"- En sık kural: {en_sik['A']} → {en_sik['B']} (destek %{en_sik['support']*100:.1f}, kaldıraç {en_sik['lift']:.2f})")
R.append(f"- En güvenilir kural: {en_guvenilir['A']} → {en_guvenilir['B']} (güven {en_guvenilir['confidence']:.2f}, kaldıraç {en_guvenilir['lift']:.2f})")
R.append(f"- En yüksek kaldıraç: {ilk5.iloc[0]['A']} → {ilk5.iloc[0]['B']} (kaldıraç {ilk5.iloc[0]['lift']:.2f}, {ilk5.iloc[0]['sepet_sayisi']:,} sepet)")
R.append(f"- Dikkat (tuzak): destek eşiği olmasaydı {ad(A_oge)} → {tuzak['oge']} kuralının kaldıracı "
         f"{tuzak['kaldirac']:.2f} çıkardı; ama yalnız {int(tuzak['birlikte_sepet'])} sepete dayanıyor. "
         f"Karar için yetersiz; Apriori'nin destek eşiği (en az {math.ceil(A['min_support']*n_sepet)} sepet) bu kuralı eledi.")
R.append("")
R.append("## 5. Karar")
R.append("Bu bölümü kod yazmaz, analist yazar. Her kural için üç soru:")
R.append("1. Kural **yeni** bir şey söylüyor mu, yoksa zaten bilineni mi? (aynı ürünün renkleri, bir filmin devamı)")
R.append("2. Kural bir **eyleme** dönüşüyor mu? (raf yerleşimi, paket, çapraz satış, 'bunu beğenen şunu da beğendi' kutusu)")
R.append("3. Kural kaç sepete dayanıyor; eyleme geçince ne kadar müşteriyi etkiler?")
R.append("")
R.append(f"Örnek: {ad(A_oge)} alan müşteriye önerilenler: "
         + (", ".join(f"{ad(o)} ({l:.2f})" for o, l in oneri.items()) if len(oneri) else "kural yok, en çok satanlara dönülür")
         + ".")
R.append("")
R.append(f"_Üretim: {time.strftime('%Y-%m-%d %H:%M')} · {VERI_SETI} · süre {time.time() - t0:.0f} sn_")

rapor = "\n".join(R)
print(rapor)
with open(os.path.join(CIKTI, "rapor.md"), "w", encoding="utf-8") as f:
    f.write(rapor + "\n")
print(f"\nDosyalar: {os.path.join(CIKTI, 'rapor.md')} · {os.path.join(CIKTI, 'kurallar.csv')}")
