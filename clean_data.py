import pandas as pd
import numpy as np

# --- 1. DATAN LATAUS JA VALMISTELU ---
# Ladataan data Excel-tiedostosta.

try:
    df = pd.read_excel('raw/sahkon-hinta-010121-061025.xlsx', header=3)
except FileNotFoundError:
    print("Tiedostoa 'sahkon-hinta-010121-061025.xlsx' ei löytynyt.")
    exit()

# Muutetaan päivämäärä datetime-objektiksi ja asetetaan se indeksiksi
df['aika'] = pd.to_datetime(df['Aika'], format='%d/%m/%Y %H:%M.%S')
df.set_index('aika', inplace=True)


# Suodatetaan data ajanjaksolle 01.01.2021 - 30.09.2025, jotta varttidata ei ole mukana
df = df[df.index < '2025-10-01']

# Muutetaan data tunnittaiseksi ottamalla tuntikeskiarvo
hourly_df = df[['Hinta (snt/kWh)']].resample('H').mean()

hourly_df.rename(columns={'Hinta (snt/kWh)': 'hinta'}, inplace=True)

# Muodostetaan ALV 0% sarake

conditions = [
    # Ehto 1: Hinta on negatiivinen (ALV on 0%)
    hourly_df['hinta'] < 0,
    
    # Ehto 2: Päivämäärä on 1.12.2022 ja 30.4.2023 välillä (ALV 10%)
    (hourly_df.index >= '2022-12-01') & (hourly_df.index <= '2023-04-30'),
    
    # Ehto 3: Päivämäärä on ennen 1.9.2024 (ALV 24%)
    hourly_df.index < '2024-09-01'
]

# 2. Määritellään laskutoimitukset, jotka vastaavat ehtoja
choices = [
    hourly_df['hinta'],                # Jos hinta negatiivinen, hinta pysyy samana
    hourly_df['hinta'] / 1.10,         # Poistetaan 10 % ALV
    hourly_df['hinta'] / 1.24          # Poistetaan 24 % ALV
]

# 3. Luodaan uusi sarake 'hinta_alv0'
# np.select käy ehdot läpi järjestyksessä. Jos mikään ehto ei täyty,
# käytetään 'default'-arvoa (nykyinen ALV 25.5%).
hourly_df['hinta_alv0'] = np.select(conditions, choices, default=hourly_df['hinta'] / 1.255)




print("Datan viisi ensimmäistä tuntia:")
print(hourly_df.head())
print("\nDatan viisi viimeistä tuntia:")
print(hourly_df.tail())

# Tallennetaan puhdistettu data csv-tiedostoon
hourly_df.to_csv('clean/sahkon_hinta_clean.csv')