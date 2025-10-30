"""
audio_eq_normalizer.py
----------------------

Yksinkertainen äänenkäsittelyskripti, joka:

1. Lukee WAV-tiedoston
2. Säätää matalia (basso) ja korkeita (diskantti) taajuuksia
   - Low-shelf ja High-shelf suotimet (RBJ Audio EQ Cookbook)
3. Normalisoi äänen tiettyyn LUFS-tasoon pyloudnorm-kirjastolla
4. Tallentaa tuloksen uuteen WAV-tiedostoon

Käyttää:
    - numpy
    - soundfile
    - pyloudnorm (https://github.com/csteinmetz1/pyloudnorm)
    - scipy.signal (biquad-suotimien laskentaan)

© 2025 – Esimerkkiskripti (vapaa käyttö)
"""

import math
import numpy as np
import soundfile as sf
import pyloudnorm as pyln
from scipy.signal import tf2sos, sosfilt

# ------------------------------------------------------------
# Tiedostopolut ja normalisoinnin tavoitetaso
# ------------------------------------------------------------
IN  = "test.wav"         # Lähdetiedosto
OUT = "test_out.wav"     # Tallennettava tiedosto
TARGET_LUFS = -14.0      # Tavoiteäänenvoimakkuus LUFS-mittayksiköissä

# ------------------------------------------------------------
# EQ-asetukset
# ------------------------------------------------------------
BASS_GAIN_DB    = +0.0    # Basson nosto (positiivinen) tai lasku (negatiivinen)
BASS_FREQ_HZ    = 100.0   # Low-shelf suotimen rajataajuus
BASS_Q          = 0.707   # Suotimen leveys, 0.707 ≈ 1/√2 = perusleveys

TREBLE_GAIN_DB  = -1.0    # Diskantin nosto/lasku (negatiivinen laskee)
TREBLE_FREQ_HZ  = 6000.0  # High-shelf suotimen rajataajuus
TREBLE_Q        = 0.707   # Suotimen leveys

print("BASS GAIN   ->", BASS_GAIN_DB, "dB")
print("TREBLE GAIN ->", TREBLE_GAIN_DB, "dB")

# ------------------------------------------------------------
# Low-shelf EQ (RBJ Audio EQ Cookbook)
# ------------------------------------------------------------
def low_shelf(fs, f0, gain_db, Q=0.707):
    """Muodostaa low-shelf (bassoboosti) suotimen"""
    A = 10**(gain_db / 40.0)
    w0 = 2 * math.pi * f0 / fs
    cosw0, sinw0 = math.cos(w0), math.sin(w0)
    alpha = sinw0 / (2 * Q)
    sqrtA = math.sqrt(A)

    # RBJ cookbook -kaavat
    b0 =    A*((A+1) - (A-1)*cosw0 + 2*sqrtA*alpha)
    b1 =  2*A*((A-1) - (A+1)*cosw0)
    b2 =    A*((A+1) - (A-1)*cosw0 - 2*sqrtA*alpha)
    a0 =        (A+1) + (A-1)*cosw0 + 2*sqrtA*alpha
    a1 =   -2*((A-1) + (A+1)*cosw0)
    a2 =        (A+1) + (A-1)*cosw0 - 2*sqrtA*alpha

    b = np.array([b0/a0, b1/a0, b2/a0])
    a = np.array([1.0, a1/a0, a2/a0])
    return tf2sos(b, a)

# ------------------------------------------------------------
# High-shelf EQ (RBJ Audio EQ Cookbook)
# ------------------------------------------------------------
def high_shelf(fs, f0, gain_db, Q=0.707):
    """Muodostaa high-shelf (diskantti) suotimen"""
    A = 10**(gain_db / 40.0)
    w0 = 2 * math.pi * f0 / fs
    cosw0, sinw0 = math.cos(w0), math.sin(w0)
    alpha = sinw0 / (2 * Q)
    sqrtA = math.sqrt(A)

    # RBJ cookbook -kaavat
    b0 =    A*((A+1) + (A-1)*cosw0 + 2*sqrtA*alpha)
    b1 = -2*A*((A-1) + (A+1)*cosw0)
    b2 =    A*((A+1) + (A-1)*cosw0 - 2*sqrtA*alpha)
    a0 =        (A+1) - (A-1)*cosw0 + 2*sqrtA*alpha
    a1 =    2*((A-1) - (A+1)*cosw0)
    a2 =        (A+1) - (A-1)*cosw0 - 2*sqrtA*alpha

    b = np.array([b0/a0, b1/a0, b2/a0])
    a = np.array([1.0, a1/a0, a2/a0])
    return tf2sos(b, a)

# ------------------------------------------------------------
# 1) Lue ääni ja muuta se double-tyyppiseksi
# ------------------------------------------------------------
data, sr = sf.read(IN, always_2d=True)
data = data.astype(np.float64)

# ------------------------------------------------------------
# 2) Käytä EQ-suodattimet: basso -> diskantti
# ------------------------------------------------------------
eq = data

# Basso (low-shelf)
if abs(BASS_GAIN_DB) > 1e-6:
    sos_low = low_shelf(sr, BASS_FREQ_HZ, BASS_GAIN_DB, BASS_Q)
    eq = np.vstack([sosfilt(sos_low, eq[:, i]) for i in range(eq.shape[1])]).T
    print(f"Applied low-shelf EQ: {BASS_GAIN_DB:+.1f} dB @ {BASS_FREQ_HZ:.0f} Hz")

# Diskantti (high-shelf)
if abs(TREBLE_GAIN_DB) > 1e-6:
    sos_high = high_shelf(sr, TREBLE_FREQ_HZ, TREBLE_GAIN_DB, TREBLE_Q)
    eq = np.vstack([sosfilt(sos_high, eq[:, i]) for i in range(eq.shape[1])]).T
    print(f"Applied high-shelf EQ: {TREBLE_GAIN_DB:+.1f} dB @ {TREBLE_FREQ_HZ:.0f} Hz")

# ------------------------------------------------------------
# 3) Mittaa äänenvoimakkuus ja normalisoi LUFS-tasoon
#    (Käyttää pyloudnorm -kirjastoa, ITU-R BS.1770-4 standardi)
# ------------------------------------------------------------
meter = pyln.Meter(sr)
measured_loudness = meter.integrated_loudness(eq)

# Normalisointi haluttuun LUFS-arvoon
normalized = pyln.normalize.loudness(eq, measured_loudness, TARGET_LUFS)

print(f"Measured loudness: {measured_loudness:.2f} LUFS -> Target: {TARGET_LUFS:.2f} LUFS")

# ------------------------------------------------------------
# 4) Tallenna tulos WAV-tiedostona (PCM 16-bit)
# ------------------------------------------------------------
sf.write(OUT, np.clip(normalized, -1.0, 1.0), sr, subtype="PCM_16")
print("✅ Processing complete!")
print("Output saved to:", OUT)
