import pandas as pd
from statsmodels.tsa.arima.model import ARIMA
from sklearn.metrics import mean_squared_error, mean_absolute_error
import numpy as np
import matplotlib.pyplot as plt

def arima_malli(tiedosto,p,d,q):
    # --- 1. Datan lataus ja valmistelu ---
    try:
        df = pd.read_csv(tiedosto)
    except FileNotFoundError:
        print(f"Tiedostoa '{tiedosto}' ei löytynyt. Varmista, että se on samassa kansiossa.")
        return

    df['aika'] = pd.to_datetime(df['aika'])
    df.set_index('aika', inplace=True)
    hinta_sarja = df['hinta_alv0']
    hinta_sarja = hinta_sarja.asfreq('h') # Asetetaan taajuudeksi tunnin välein
    hinta_sarja.ffill(inplace=True) # Täytetään mahdolliset aukot

    # --- 2. Datan jako opetus- ja testijoukkoihin ---
    # Ennustetaan viimeinen viikko (7 * 24 tuntia)
    train_size = len(hinta_sarja) - (7 * 24)
    train_data, test_data = hinta_sarja[0:train_size], hinta_sarja[train_size:]

    print(f"Opetusdatan koko: {len(train_data)} havaintoa")
    print(f"Testidatan koko: {len(test_data)} havaintoa")

    # --- 3. Mallin opettaminen ---
    # ARIMA(p,d,q) - perinteinen malli ilman kausivaihtelua
    # Valitut parametrit (5,1,0) ovat yleinen lähtökohta
    model = ARIMA(train_data, order=(p, d, q))
    print("Opetetaan ARIMA-mallia...")
    model_fit = model.fit()

    # --- 4. Ennusteen tekeminen ---
    predictions = model_fit.forecast(steps=len(test_data))

    # --- 5. Tulosten arviointi ---
    mse = mean_squared_error(test_data, predictions)
    rmse = np.sqrt(mse)
    mae = mean_absolute_error(test_data, predictions)

    print("\n--- ARIMA-mallin tulokset ---")
    print(f"RMSE (neliöllinen keskiarvovirhe): {rmse:.4f}")
    print(f"MAE (keskimääräinen absoluuttinen virhe): {mae:.4f}")

    # --- 6. Visualisointi ---
    plt.figure(figsize=(15, 7))
    plt.title(f'ARIMA-ennuste vs. Todellinen hinta (p={p}, d={d}, q={q})')
    plt.plot(train_data.index[-200:], train_data[-200:], label='Opetusdata (osa)')
    plt.plot(test_data.index, test_data, label='Todelliset arvot (testidata)', color='blue')
    plt.plot(test_data.index, predictions, label='ARIMA-ennuste', color='red', linestyle='--')
    plt.xlabel('Aika')
    plt.ylabel('Hinta (ALV 0%)')
    plt.legend()
    plt.grid(True)
    plt.show()
    plt.savefig(f'figures/arima_ennuste_p{p}_d{d}_q{q}.png')

arima_malli("clean/sahkon_hinta_clean.csv",5,1,0)