# 🎧 audio_eq_normalizer.py

Yksinkertainen, käytännöllinen **äänenkäsittelyskripti**:

1. **Lukee** WAV-tiedoston  
2. **Säätää** taajuusbalanssia:
   - **Low-shelf** (basso) RBJ Audio EQ Cookbook -suotimella  
   - **High-shelf** (diskantti) RBJ Audio EQ Cookbook -suotimella  
3. **Normalisoi** äänen **LUFS-tasoon** standardin ITU-R BS.1770 mukaisesti käyttäen [`pyloudnorm`](https://github.com/csteinmetz1/pyloudnorm)-kirjastoa  
4. **Tallentaa** tuloksen uuteen WAV-tiedostoon

> 💡 **Käyttötarkoitus:** nopea “pre-masterointi” tai sisällöntuotannon perus-EQ + LUFS-normalisointi (YouTube, podcast, demot).

---

## ⚙️ Vaatimukset

- Python 3.9 tai uudempi  
- Kirjastot:
  - `numpy`
  - `soundfile` (libsndfile)
  - `pyloudnorm` (tested 0.1.1)
  - `scipy`

Asennus:

```bash
pip install numpy soundfile pyloudnorm scipy
```

> 🎵 **MP3-vientiin** tarvitset erikseen [FFmpeg](https://ffmpeg.org/):n (ei pakollinen tälle skriptille).

---

## 📄 Tiedosto

`audio_eq_normalizer.py` (esimerkkikonfiguraatiot koodin alussa):

```python
IN  = "test.wav"
OUT = "test_out.wav"
TARGET_LUFS = -14.0

# EQ-asetukset
BASS_GAIN_DB    = +0.0   # basso: +dB nostaa, 0.0 = pois
BASS_FREQ_HZ    = 100.0
BASS_Q          = 0.707

TREBLE_GAIN_DB  = -1.0   # diskantti: NEGATIIVINEN laskee (esim. -3 dB)
TREBLE_FREQ_HZ  = 6000.0
TREBLE_Q        = 0.707
```

---

## ▶️ Käyttö

1. **Aseta lähde ja kohde**
   ```python
   IN  = "polku/input.wav"
   OUT = "polku/output.wav"
   ```

2. **Säädä EQ (valinnaista)**

   | Säädin            | Kuvaus                                   | Tyypillinen arvo |
   |:------------------|:-----------------------------------------|:-----------------|
   | `BASS_GAIN_DB`    | lisää tai vähennä matalia                | `0 … +6 dB`      |
   | `TREBLE_GAIN_DB`  | lisää/vähennä korkeita (neg. = leikkaa)  | `-2 … -6 dB`     |
   | `BASS_FREQ_HZ`    | basson rajataajuus                       | 80–120 Hz        |
   | `TREBLE_FREQ_HZ`  | diskantin rajataajuus                    | 5–8 kHz          |
   | `Q`               | suotimen leveys                          | 0.707            |

3. **Valitse LUFS-tavoite**
   - YouTube: `TARGET_LUFS = -14.0`  
   - Podcast / puhe: `-16 … -18 LUFS`

4. **Aja**
   ```bash
   python audio_eq_normalizer.py
   ```
   Tuloste kertoo mitatun LUFS-arvon ja normalisoinnin.  
   Valmis tiedosto tallennetaan `OUT`-polkuun.

---

## 🔬 Miten tämä toimii

- **EQ**: toteutettu **RBJ Audio EQ Cookbook** -biquad-kaavoilla (low / high-shelf) ja sovellettu kanavittain `scipy.signal.sosfilt`-suodattimella  
- **LUFS**: mitataan `pyloudnorm.Meter.integrated_loudness()` ja taso säädetään `pyln.normalize.loudness()`-funktiolla  
- **Dataformaatti**: aina 2D-matriisi `(N, C)` ja float-skaalaus `[-1 … +1]`

---

## 🪟 Huomiot Windows-ympäristössä

`soundfile` / `libsndfile` saattaa **kompastua Unicode-emojiin** tai **UNC-verkko­polkuihin**, mikä johtaa virheeseen *“Error opening … System error”*.

**Ratkaisu:**
- kirjoita ensin paikalliseen temp-kansioon (esim. `C:\Temp`) ja siirrä valmis WAV kohteeseen  
- vältä emoji- ja erikoismerkkejä tiedosto- ja kansio­nimissä

---

## 🧩 Ongelmanratkaisu

- **“Error opening ‘…wav’: System error”**  
  → Tallenna ensin `C:\Temp\out.wav` ja siirrä siitä kohteeseen.  

- **Yli-/aliklippaus**  
  → Skripti klippaa varmuuden vuoksi arvoihin `[-1.0, 1.0]`, mutta huomaa että **LUFS-normalisointi ei ole limiteri**.  
  Tarvittaessa lisää erillinen limiteri (esim. FFmpeg / DAW).

---

## 🎚️ Turvalliset aloitusarvot

| Säädin              | Arvo        |
|:--------------------|:------------|
| **BASS_GAIN_DB**    | +3.0 dB     |
| **BASS_FREQ_HZ**    | 100 Hz      |
| **TREBLE_GAIN_DB**  | -3.0 dB     |
| **TREBLE_FREQ_HZ**  | 6000 Hz     |
| **TARGET_LUFS**     | -14.0 LUFS  |

---

## 📚 Lähteet & Kiitokset

- [**pyloudnorm**](https://github.com/csteinmetz1/pyloudnorm) — ITU-R BS.1770-4 loudness-toteutus Pythonissa  
- **RBJ Audio EQ Cookbook** – Biquad-suodinten kaavat  
  *Robert Bristow-Johnson, “Cookbook formulae for audio equalizer biquad filter coefficients”*

---

## 🪪 Lisenssi

Tämä skripti on vapaa käytettäväksi ja muokattavaksi.  
Lisää tarvittaessa oma **LICENSE**-tiedosto (esim. MIT tai Apache 2.0).

---
