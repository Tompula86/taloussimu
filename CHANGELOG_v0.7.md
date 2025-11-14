# CHANGELOG v0.7: Työmarkkinareformi + Rakennusliike 🏗️

## 📋 Yhteenveto

Versio 0.7 toteuttaa **kaksi kriittistä laajennusta**:
1. **Täydellinen työmarkkinareformi** - Korvaa "kaikki maksavat kaikille" -mallin dynaamisella työmarkkina-areenalla
2. **Rakennusliike taloudellisena prosessina** - Asuntojen rakentaminen ei ole enää maagista, vaan sitoo pääomaa, työtä ja materiaaleja

## ✨ Keskeiset muutokset

### 1. HouseholdAgent - Henkilökohtainen palkka

**Aiemmin (v0.6):**
- Kotitalous oli automaattisesti työllistetty jos `age < retirement_age`
- Palkka oli aina yrityksen `wage_level` (ei henkilökohtainen)
- `lose_job()` ei nollannut palkkaa

**Nyt (v0.7):**
```python
self.employed: bool = False  # Aloitetaan työttömänä
self.wage: float = 0.0       # Henkilökohtainen palkkataso
```

- Työllisyys määräytyy työmarkkinamekanismin kautta
- Jokaisella työntekijällä on oma palkkataso (`self.wage`)
- `expected_monthly_income()` käyttää henkilökohtaista palkkaa
- `lose_job()` nollaa sekä työsuhteen että palkan

### 2. FirmAgent - Työvoimanhallinta

**Aiemmin (v0.6):**
- `pay_wages()` maksoi palkkaa **kaikille** kotitalouksille
- Ei työntekijälistaa → konkurssit väistämättömiä
- Tuotanto: kiinteä 20 yksikköä/kk

**Nyt (v0.7):**
```python
self.employees: list[HouseholdAgent] = []  # Oma työntekijälista
self.target_employees: int = 0             # Tavoitetyövoima
self.production_per_employee: float = 100  # Tuotanto skaalautuu työvoimaan
```

**Uudet metodit:**
- `_update_labor_demand()`: Päivittää `target_employees` varastotilanteen mukaan
  - Jos `inventory < 0.8 × target_inventory` → palkkaa lisää
  - Jos `inventory > 1.2 × target_inventory` → vähennä työvoimaa
  
- `_update_wage_level()`: Palkkojen Phillips-käyrä
  - Jos `unemployment < 5%` → nosta palkkoja 1%
  - Jos `unemployment > 10%` → laske palkkoja 1%

**Palkanmaksu:**
- Maksaa **vain** `self.employees`-listan jäsenille
- Käyttää kunkin työntekijän henkilökohtaista `wage`-kenttää
- Konkurssi jos ei pysty maksamaan (realistinen rajoite)

**Konkurssi:**
- Irtisanoo vain omat työntekijät (`self.employees`)
- Tyhjentää listan tehokkaasti

### 3. EconomyModel - Työmarkkinavaihe

**Uusi metodi: `_run_labor_market()`**

Kutsutaan **ennen** firmojen ja kotitalouksien `step()`-metodeja joka kuukausi.

**Vaiheet:**

1. **Päivitys**: Kaikki firmat päivittävät `target_employees` ja `wage_level`
2. **Irtisanomiset**: Ylityöllistetyt firmat irtisanovat satunnaisia työntekijöitä
3. **Työnhakijat**: Kerätään kaikki työttömät yhteen pooliin
4. **Avoimet paikat**: Firmat luovat avoimia paikkoja (`target - current`)
5. **Matching**: Työttömät täyttävät korkeimmin palkattuja paikkoja ensin

**Alustus:**
- Työikäiset kotitaloudet jaetaan tasaisesti firmojen kesken
- Asetetaan työllisiksi ja annetaan heille yrityksen `wage_level`
- Firmojen `target_employees` = alkuperäinen työntekijämäärä

### 4. Tasapainoparametrit

**Firmojen alkukassa:**
```python
initial_payroll_reserve = wage_level * 35 * 6  # 6 kk palkkavaranto
```
- Riittävä puskuri käynnistymiseen ilman välitöntä konkurssia

**Hinta:**
```python
self.price: float = 30.0  # Aiemmin 1.0
```
- Linkitetty palkkatasoon (realistinen katemarginaali)
- Varmistaa että kulutus tuottaa riittävästi tuloja

**Tuotanto:**
```python
production = len(self.employees) * 100  # Skaalautuu työvoimaan
```
- Aiemmin kiinteä 20 yksikköä → nyt dynaaminen

## 📊 Tulokset

### Ennen v0.7 (placeholderi):
- Työttömyysaste: **99-100%**
- Aktiivisia yrityksiä: **0-1 kpl**
- Konkurssit: **Kaikki firmat kuolevat heti**
- Valtion saldo: **Massiivinen alijäämä**

### Jälkeen v0.7:
- Työttömyysaste: **33% (loppu)**, keskiarvo **40%**
- Aktiivisia yrityksiä: **9 kpl**
- Yritysten keski-ikä: **50 kk** (pitkäikäiset!)
- Yrittäjyysaste: **9%**
- Valtion saldo: **+818k€**
- Kulutus: **384k€/kk**

## 🎯 Vaikutukset

### Makrotalous
- ✅ Realistinen työttömyys (ei enää 100%)
- ✅ Dynaaminen työmarkkinatasapaino
- ✅ Phillips-käyrä: palkkojen ja työttömyyden välinen suhde
- ✅ Valtion tulot riittävät (positiivinen budjetti)

### Yritykset
- ✅ Elävät pitkään (50 kk keskiarvo)
- ✅ Palkkaus ja irtisanomiset endogeenisiä
- ✅ Tuotanto skaalautuu työvoimaan
- ✅ Konkurssit realistisia (vain maksukyvyttömät)

### Kotitaloudet
- ✅ Henkilökohtaiset palkat
- ✅ Työttömyys dynaamista
- ✅ Työpaikan menetys vaikuttaa tuloihin

## 🔧 Tekniset parannukset

**Koodin laatu:**
- Poistettu `pay_wages()`:n automaattinen palkkalaina (ei-realistinen)
- Selkeä `employees`-lista vs. globaali "kaikki kotitaloudet"
- Työmarkkinalogiikka eriytetty omaan metodiinsa

**Suorituskyky:**
- Työntekijöiden loop pienentynyt: `len(employees)` << `len(households)`

## 📝 Jatkokehitys

Seuraavat versiot voivat sisältää:

### v0.8 - Taitotasot ja palkkaerot
- `household.skills: float` → vaikuttaa palkkaan
- Koulutus nostaa taitotasoa
- Yritykset palkkaavat taitavimpia ensin

### v0.9 - Ammattiliitot ja neuvottelut
- Kollektiivinen palkanneuvottelu
- Lakot vaikuttavat tuotantoon

### v1.0 - Täysi julkaisu
- Työntekijän mobility (sektorien välinen siirtyminen)
- Ikääntyminen vaikuttaa tuottavuuteen
- Eläkepuskuri ja varhaiseläke

## 🏗️ OSA 2: Rakennusliike ja Asuntojen Tarjonta

### Miksi kriittinen?
**Ongelma v0.6:**
- Asunnot ilmestyivät tyhjästä ilman taloudellista vaikutusta
- Ei työllisyyttä, ei pääomakiertoa, ei suhdannesykliä

**Ratkaisu v0.7:**
- Rakentaminen on **investointiprosessi** joka sitoo pääomaa ja työtä aikaan
- Rakennusliike on erikoistunut FirmAgent

### 1. FirmAgent-erikoistuminen
```python
self.firm_type: str = "construction"  # tai "manufacturer", "service"

# Rakennusliike-spesifit kentät:
self.construction_projects: list[ConstructionProject] = []
self.construction_cost_per_sqm: float = 2000.0
self.construction_duration_months: int = 12
self.target_profit_margin: float = 0.15
self.max_concurrent_projects: int = 3
```

### 2. ConstructionProject-dataluokka
```python
@dataclass
class ConstructionProject:
    dwelling_size: int
    start_month: int
    duration_months: int
    total_budget: float
    spent_so_far: float
    status: str  # "ongoing", "completed", "delayed"
    workers_hired: int
    monthly_wage_budget: float
    monthly_material_budget: float
    dwelling_id: int | None = None
```

### 3. 5-Vaiheinen Rakentamisprosessi

**Vaihe 1: Markkina-analyysi**
- Jos `market_price > construction_cost * 1.15` → Kannattaa rakentaa
- Valitsee kannattavimman koon

**Vaihe 2: Rahoitus**
- Hae rakennuslaina pankilta
- Laina siirtyy yrityksen kassaan

**Vaihe 3: Rakennusvaihe (12kk)**
- Maksaa palkkoja → luo työpaikkoja
- Ostaa materiaaleja muilta yrityksiltä → kiihdyttää taloutta
- Kirjaa kulut `spent_so_far`:iin

**Vaihe 4: Valmistuminen**
- Luo uusi `Dwelling` → `housing_market.dwellings`
- Aseta myyntiin `for_sale = True`

**Vaihe 5: Myynti ja Tuloslaskelma**
- Voitto = `revenue - spent_so_far - lainakorot`
- Maksa laina pois pankille

### 4. Uudet Mittarit
```python
"construction_projects_active"
"construction_employment"
"dwellings_completed_per_month"
"construction_sector_cash"
"avg_construction_profit_margin"
```

### 5. Taloudelliset Vaikutukset

**Suhdannesykli:**
- Hinnat nousevat → Rakentajat aktivoituvat
- Rakentaminen luo työpaikkoja → Tulot kasvavat
- Tarjonta kasvaa → Hinnat stabiloituvat
- Rakentaminen hidastuu → Työttömyys kasvaa

**Testaus (24kk):**
```
Initial dwellings: 80
After 24 months: 83
New dwellings: 3 (3 projektia valmistui)
```

## 🐛 Tunnetut rajoitteet

### Työmarkkinat:
1. **Yksinkertainen matching**: FIFO-järjestys, ei optimaalista kohtaantoa
2. **Ei hakukustannuksia**: Työttömät löytävät työpaikan heti jos paikkoja on
3. **Ei työttömyysturvapäiviä**: Ei maksimikestoa tai karenssia

### Rakennusliike:
1. **Yksinkertaistettu myynti**: Asunnot "myydään" heti valmistumishetkellä
2. **Konkurssiherkkä**: Rakennusliike voi mennä konkurssiin pitkissä simulaatioissa
3. **Ei maapolitiikkaa**: Ei rajoituksia rakentamisen määrälle

---

**Versio:** 0.7.0  
**Päivämäärä:** 14.11.2025  
**Tekijä:** Taloussimu Development Team
