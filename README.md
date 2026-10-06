# CENG468 Veri Madenciliği

Pamukkale Üniversitesi · Mühendislik Fakültesi · 2026-2027 Güz
Öğr. Gör. Dr. Duygu TOPALOĞLU

Bu repoda dersin **kodları** (`Kodlar/`), **sunumları** (`Sunumlar/`) ve çalışma ortamının tarifi bulunur. Aşağıdaki kurulumu **bir kez** yaparsınız; sonra her hafta yalnızca güncellemeleri alırsınız.

> Windows ve Mac için komutlar aynıdır. Farklı olduğu yerde ikisi de yazılıdır. Komutları **VS Code'un terminaline** yazın (Windows'ta bu PowerShell'dir).

---

## Kurulum (bir kez, ~15 dk)

### 1. VS Code ve eklentiler
1. VS Code'u kurun: <https://code.visualstudio.com>
2. Sol çubuktan **Extensions**'ı açın (`Ctrl+Shift+X`, Mac: `Cmd+Shift+X`). Yayıncısı **Microsoft** olan iki eklentiyi kurun: **Python** ve **Jupyter**.

### 2. uv'yi kurun
uv, dersin Python ortamını kuran araçtır. Anaconda veya ayrı bir Python kurmanız **gerekmez**.

- **Windows** (PowerShell):
  ```powershell
  powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
  ```
- **Mac** (Terminal):
  ```bash
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```

Bitince **terminali kapatıp yeniden açın** ve kontrol edin: `uv --version` → `uv 0.x.x` gibi bir sürüm görmelisiniz.

### 3. Git'i kontrol edin
```
git --version
```
Sürüm yazıyorsa geçin. Yazmıyorsa: **Windows**'ta <https://git-scm.com/download/win> adresinden indirip varsayılan ayarlarla kurun. **Mac**'te komut sizden "Command Line Developer Tools" kurulumunu ister; **Yükle** deyin.

### 4. Ders klasörünü indirin
```
cd ~
git clone https://github.com/duygutopaloglu/CENG468.git ceng468
```
Klasör kullanıcı klasörünüzde oluşur: Windows `C:\Users\<adınız>\ceng468`, Mac `/Users/<adınız>/ceng468`.

> ⚠️ **Masaüstü, Belgeler, OneDrive, iCloud veya Google Drive kullanmayın.** Bu klasörler senkronize edilir ve senkronizasyon ortam klasörünü (`.venv`) bozar.

### 5. Ortamı kurun
1. VS Code'da **File → Open Folder** ile `ceng468` klasörünü açın. "Do you trust the authors…" sorulursa **Yes, I trust the authors** deyin.
2. **Terminal → New Terminal** ile terminali açın ve çalıştırın:
   ```
   uv sync
   ```
3. Şuna benzer satırlar görmelisiniz (sayılar ve süreler sizde biraz farklı olabilir):
   ```
   Creating virtual environment at: .venv
   Resolved 67 packages in ...
   Installed 61 packages in ...
   ```
   Python'unuz yoksa önce `Downloading cpython-3.13…` satırı da görünür; bu normaldir.

### 6. Veriyi indirin
`Veri/online_retail/BENIOKU.md` dosyasını açın ve oradaki adımları izleyin. Veri dosyaları repoda **yoktur**; her öğrenci kendisi indirir.

### 7. Kurulumu test edin
1. `Kodlar/00_kurulum_testi.ipynb` dosyasını açın.
2. Sağ üstte **Select Kernel**'e basın. Listeden **⭐ Recommended** etiketli, yolu **`.venv`** ile başlayan ortamı seçin (adı `ceng468 (3.13…)` görünür).
   > ⚠️ Listede aynı adlı başka ortamlar (örn. Anaconda'dan kalma `ceng468`) olabilir. **Ada değil, yola bakın:** Mac `.venv/bin/python`, Windows `.venv\Scripts\python.exe`.
3. Hücreleri `Shift+Enter` ile çalıştırın. İlk çalıştırma **30–60 saniye** sürebilir, bekleyin.
4. **✅ Kurulum tamam!** yazısını görüyorsanız hazırsınız.

---

## Derste çalışma kuralı: önce kopyala

`Kodlar/` içindeki dosyaları **doğrudan değiştirmeyin.** Hoca bu dosyaları güncellediğinde sizin değişiklikleriniz `git pull` komutunu durdurur.

Ders başında notebook'un **kopyasını** alın ve kopyada çalışın: Explorer'da dosyaya sağ tık → **Copy** → **Paste** → kopyayı istediğiniz adla yeniden adlandırın (örn. `H03_notlarim.ipynb`). Kopyalarınızı istediğiniz klasörde tutabilirsiniz.

## Her hafta: güncellemeleri alın
```
git pull
uv sync
```
`git pull` yeni dosyaları getirir, `uv sync` yeni paket varsa kurar (yoksa bir şey yapmaz).

---

## Klasör yapısı

| | Ne | Siz |
|---|---|---|
| `Kodlar/`, `Sunumlar/` | Ders kodları ve sunumlar | Okuyun, **kopyalayarak** çalışın |
| `Veri/` | Her veri seti kendi klasöründe, indirme talimatıyla | Veriyi buraya koyun |
| `pyproject.toml`, `uv.lock`, `.python-version` | Ortamın tarifi (paketler ve tam sürümleri) | Dokunmayın |
| `.venv/`, `.vscode/`, `.gitignore` | Araçların kendi dosyaları | Dokunmayın |

## Altın kurallar
1. **`pip install` ve `conda install` kullanmayın.** Paketler yalnızca `uv sync` ile gelir; herkesin ortamı aynı kalır.
2. Terminalde satır başında `(base)` görüyorsanız Anaconda açıktır. `uv` komutları yine doğru çalışır; yalnızca `pip` yazmayın.
3. Notebook'ta kernel her zaman yolu **`.venv`** olan ortam olmalı.
4. Bir şey bozulursa: `.venv` klasörünü silin ve `uv sync` çalıştırın. Ortam baştan kurulur.

## Sorun giderme

| Sorun | Çözüm |
|---|---|
| `uv` / `git` tanınmıyor | Terminali (gerekirse VS Code'u) kapatıp açın. |
| Windows'ta *running scripts is disabled* | PowerShell'de bir kez: `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` |
| Kernel listesinde `.venv` yok | `Ctrl+Shift+P` (Mac `Cmd+Shift+P`) → **Developer: Reload Window**, sonra tekrar **Select Kernel**. |
| `ModuleNotFoundError` | Kernel `.venv` mi? Öyleyse terminalde `uv sync`, notebook'ta **Restart**. |
| "Excel dosyası var mı? False" | Veri dosyası `Veri/online_retail/` içinde değil; `BENIOKU.md`'ye bakın. |
| `git pull` *local changes would be overwritten* diyor | `Kodlar/` içindeki bir dosyayı değiştirmişsiniz. Değişikliğinizi kopya bir dosyaya alın, sonra hocaya danışın. |
| Eski Intel Mac'te `scikit-surprise` kurulmuyor | `xcode-select --install`, sonra tekrar `uv sync`. |

Çözemediğiniz hatada mesajın **ekran görüntüsünü** hocaya iletin.
