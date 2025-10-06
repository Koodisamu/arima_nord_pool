import pandas as pd
from statsmodels.tsa.statespace.sarimax import SARIMAX
import matplotlib.pyplot as plt
from sklearn.metrics import mean_squared_error
import numpy as np

# --- 1. DATAN LATAUS JA VALMISTELU ---
# Ladataan data Excel-tiedostosta.
# Oleta, että tiedostossa on sarakkeet 'pvm' ja 'hinta'.
try:
    df = pd.read_excel('sahkon_hinta.xlsx')
except FileNotFoundError:
    print("Tiedostoa 'sahkon_hinta.xlsx' ei löytynyt. Varmista, että tiedosto on oikeassa kansiossa.")
    exit()

# Muutetaan päivämäärä datetime-objektiksi ja asetetaan se indeksiksi
df['pvm'] = pd.to_datetime(df['pvm'])
df.set_index('pvm', inplace=True)

# Varmistetaan, että data on tunneittain ja täytetään mahdolliset pienet aukot
hourly_data = df['hinta'].asfreq('h', method='ffill')
hourly_data = hourly_data.dropna()

print("Datan viisi ensimmäistä tuntia:")
print(hourly_data.head())

# Jaetaan data opetus- ja testijoukkoihin
# Käytetään kaikkea paitsi viimeistä 7 päivää (7 * 24 tuntia) opetukseen
train_data = hourly_data[:-(7*24)]
test_data = hourly_data[-(7*24):] # Viimeiset 7 päivää

print(f"\nOpetusdata sisältää {len(train_data)} tuntia.")
print(f"Testidata sisältää {len(test_data)} tuntia.")


# --- 2. ENNUSTEEN TEKEMINEN (SARIMAX) ---
# Määritellään SARIMAX-malli.
# order=(p,d,q) on ei-kausittainen osa (kuten ARIMA)
# seasonal_order=(P,D,Q,s) on kausittainen osa
# s=24 kertoo, että kausivaihtelun jakso on 24 tuntia.
model = SARIMAX(train_data,
                order=(2, 1, 2),
                seasonal_order=(1, 1, 1, 24))

print("\nSovitetaan mallia... (tämä voi kestää hetken)")
model_fit = model.fit(disp=False)

# Tehdään ennuste testijakson ajalle (seuraavat 7 päivää)
predictions = model_fit.forecast(steps=len(test_data))

print("\nEnnusteet tehty.")


# --- 3. TOTEUMAN JA ENNUSTEEN PLOTTAAMINEN ---
plt.figure(figsize=(15, 7))
# Plotataan vain viimeiset 2 viikkoa datasta, jotta kuvaaja pysyy selkeänä
plt.plot(hourly_data.index[-((14)*24):], hourly_data[-((14)*24):], label='Toteutunut hinta')
plt.plot(predictions.index, predictions, label='Ennuste', color='red', linestyle='--')

plt.title('Sähkön tuntihinnan ennuste vs. toteuma')
plt.xlabel('Päivämäärä ja aika')
plt.ylabel('Hinta (c/kWh)')
plt.legend()
plt.grid(True)
plt.show()


# --- 4. VIRHEEN LASKEMINEN ---
mse = mean_squared_error(test_data, predictions)
rmse = np.sqrt(mse)
print(f'\nEnnusteen neliöllinen keskiarvovirhe (RMSE): {rmse:.2f}')


# --- 5. & 6. PARAMETRIEN HAKU (HUOMIO) ---
# HUOM: SARIMAX-mallin parametrien systemaattinen haku on hidasta.
# Alla on kommentoitu esimerkki, miten sen voisi tehdä, mutta sen ajaminen
# voi kestää hyvin kauan. Alussa käytetyt (2,1,2) ja (1,1,1,24) ovat yleensä
# hyviä lähtökohtia.

print("\nParametrien haku on hidasta, joten sitä ei ajeta tässä esimerkissä.")
# Esimerkki hakusilmukasta:
# best_rmse = float('inf')
# best_order = None
# ... silmukat p,d,q,P,D,Q arvoille ...
#   try:
#     model = SARIMAX(...)
#     ...
#   except:
#     continue