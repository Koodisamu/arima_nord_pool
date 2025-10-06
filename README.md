# Sarimax Nord Pool

Ladataan Nord Pool pörssisähkön Suomen aluehinnat ajanjaksolta 1.1.2021 - 7.10.2025. Lähde: https://porssisahko.net/tilastot

Putsataan data (clean_data.py):
- Muutetaan Aika -kolumni datetime muotoon, asetetaan indeksiksi
- Poistetaan varttimuotoinen data, eli 1.10.25 ->
- Muutetaan tuntidataksi ottamalla keskiarvo tunneittain
- Muodostetaan alv 0% -kolumni vertailukelpoisuuden saavuttamiseksi, logiikka: https://porssisahko.net/info

