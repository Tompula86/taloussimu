# Taloussimulaattori

Agenttipohjainen, monitasoinen taloussimulaattori modernista pankkikeskeisestä markkinataloudesta.

## Tavoite

Rakentaa avoin "talouslaboratorio", jossa voi:
- testata eri politiikkasääntöjä ja sääntelyä
- tutkia eriarvoisuuden ja velkaantumisen dynamiikkaa
- simuloida kriisiskenaarioita (korkoshokki, asuntokuplan puhkeaminen, pankkikriisi)

## Projektin rakenne

```
taloussimu/
├── agents/          # Agenttityypit (kotitalous, yritys, pankki, valtio, keskuspankki)
├── config/          # YAML-konfiguraatiotiedostot
├── core/            # Simulaation ydinlogiikka (model, config)
├── io/              # Datan tallennus ja mittarit
├── markets/         # Markkinat (hyödyke, asunto, myöhemmin LOB)
├── policy/          # Politiikka- ja verosäännöt
└── scripts/         # Ajoskriptit
```

## Asennus ja käyttö

### 1. Luo virtuaaliympäristö ja asenna riippuvuudet

```powershell
cd C:\Python\taloussimu
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 2. Aja perussimula aatio

```powershell
# Projektin juuresta, käyttäen .venv:n pythonia:
.\.venv\Scripts\python.exe -m scripts.run_minimal
```

Tämä ajaa 120 kuukauden simulaation `config/base.yaml`-konfigilla ja tulostaa perustilastot.

### 3. Muokkaa konfiguraatiota

Muokkaa `config/base.yaml`:ia säätääksesi:
- Agenttimäärät (`agents.households`, `agents.firms`)
- Palkkataso (`wages.initial`)
- Verot (`taxes.income_flat_rate`, `taxes.vat_rate`)
- Tulonsiirrot (`transfers.unemployment_benefit`, `transfers.pension`)
- **Demografiset parametrit**:
  - `households.birth_rate_per_year` – syntyvyys per henkilö per vuosi
  - `households.death_prob_per_year` – kuolleisuus per henkilö per vuosi
  - `households.fertile_age_min` / `fertile_age_max` – hedelmällinen ikä
  - `households.retirement_age` – eläkeikä
  - `households.max_age` – maksimi-ikä
  - `households.debt_service_income_share` & `households.debt_service_buffer_multiplier` – kuinka suuri osa tuloista varataan velanhoitoon ennen kulutusta
- **Yritysten investoinnit**:
  - `firms.investment_interval_months` – kuinka usein yritys hakee investointilainan
  - `firms.investment_loan_amount` ja `firms.investment_loan_term` – perusinvestoinnin koko ja laina-aika
  - `firms.investment_cash_buffer` – vähimmäiskassa ennen investointia (0 = aina sallittu)

### 4. Aja skenaarioita

```powershell
# Pitkän aikavälin simulaatio (50 vuotta)
.\.venv\Scripts\python.exe -m scripts.run_scenario --config config/long_run.yaml --output results/long_run.csv
```

### 5. Aja pankkitestit

```powershell
.\.venv\Scripts\python.exe -m pytest
```

Testit varmistavat pankkijärjestelmän velanhoitologiikan ja M1≈luottokanta -regression ilman defaultteja.

## Versiot (roadmap)

- **v0.1** ✅ – Perussykli: kotitaloudet, yritykset, valtio; palkat, verot, kulutus
- **v0.2** 🔄 – Elinkaari, taseet, perinnöt
- **v0.3** – Pankit ja endogeeninen raha
- **v0.4** – Asuntomarkkina ja asuntolainat
- **v0.5** – Yrittäjyys ja konkurssit
- **v0.6** – Realistisempi verotus ja budjetti
- **v0.7** – Kattava mittaripaketti ja validointi
- **v0.8** – Rahoitusmarkkinoiden LOB-mikrorakenne
- **v0.9** – Kalibrointi ja herkkyysanalyysi

Katso `roadmap.md` ja `suunnitelma.md` lisätietoja varten.

## Kehitystyö

Projekti käyttää Mesa 3.x -kirjastoa agenttipohjaiseen mallinnukseen. Kaikki parametrit luetaan YAML-konfiguraatioista modulaarisesti.

## Lisenssi

(Lisää myöhemmin, jos julkaistaan)
