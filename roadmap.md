Ehdotettu eteneminen (roadmap, versio 0.x)
Tämä on nimenomaan “mitä tehdään missä järjestyksessä Pythonilla”.

Projektirakenne ja perustyökalut (päivä 1–2)

Luo perusrakenne (voit tehdä käsin tai apply_patch):
core/ – kello ja simulaation runko
agents/ – kotitalous, yritys, pankki, valtio, keskuspankki
markets/ – hyödykemarkkina (myöhemmin LOB), asuntomarkkina
policy/ – verotus, tulonsiirrot, rahapolitiikan reaktiosääntö
io/ – tulosten tallennus (aluksi CSV, myöhemmin Parquet)
scripts/ – ajoskriptit, kokeet
Lisää pyproject.toml tai requirements.txt vähintään: mesa, numpy, pandas, matplotlib.
Sovi tyylisäännöt: yksinkertainen ruff/black tai vain pep8-henkinen tyyli.
Yksinkertainen Mesa-pohjainen makrosimulaation runko (v0.1)
Tavoite: yksi kuukausisykli ilman pankkirahaa, asuntoja tai LOB:ia.

Toteuta core/model.py:
EconomyModel(Mesa Model) joka pyörittää kuukausiaskelta.
Agentit (hyvin yksinkertaiset versiot):
HouseholdAgent: tila: ikä, työssä/työtön, palkka, käteinen. Päätökset: kuluta vs. säästä.
FirmAgent: tila: kasa palkkoja, työntekijät, hyödykkeen hinta. Päätökset: palkkaa/irtisano, tuota ja myy.
StateAgent: kerää tuloveron ja ALV:n, maksaa työttömyystukea ja eläkkeitä.
Yksinkertainen kuukausisykli (versio “minimal”):
Palkat ja verot
Tulonsiirrot (tuet, eläkkeet)
Kulutus & hyödykemarkkina (ei vielä dynaamista hintaa)
Firmojen voitot ja yksinkertainen investointipäätös.
Tallennus: jokaisesta kuukaudesta DataCollector: Gini varallisuudelle, työttömyys, valtion alijäämä.
Elinkaari, perinnöt ja taseet (v0.2)
Tavoite: kotitalouksista tulee “oikeita” taseagentteja.

Laajenna HouseholdAgent:
Tase: käteinen, reaaliomaisuus (placeholder), yritysomistus (placeholder), velat.
Ikääntyminen, kuolema, perintö (perillisten valinta yksinkertaisella säännöllä).
Lisää syntymät/nuoret agentit, jotka tulevat työmarkkinoille tietystä iästä eteenpäin.
Päivitä Gini-laskenta nettovarallisuudelle.
Pankit, velka ja endogeeninen raha (v0.3)
Tavoite: toteuttaa pankkijärjestelmä, jossa velka luo talletuksia.

Uusi agentti: BankAgent (v0.3a)
- Tase: talletukset, lainat, kassavarat, oma pääoma + erillinen "default bucket".
- Parametrit: talletus- ja lainakorot, korkomarginaali, min. pääomasuhde, likviditeettipuskuri, hyväksymissäännöt (LTV/LTI + maksukykyyn perustuva maksimiannuiteetti), maks. luottokanta per agentti.
- Prosessi: `request_loan(agent, amount, purpose, maturity_months)` → hyväksyntä kirjataan sekä lainasaamiseksi (aktiva) että talletusvastuuksi (passiva).

Luottosykli ja kuukausittaiset eventit (v0.3b)
- Kotitaloudet ja firmat tekevät lainahakemuksen ennen kulutus-/palkkapäätöksiä.
- BankAgent muodostaa annuiteettiaikataulun (korko + lyhennys) ja veloittaa maksun kuukausittain ennen kotitalouksien kulutusta; firmoille ennen palkkoja.
- Jos agentti ei pysty maksamaan, velka siirtyy default-tilaan ja pankin oma pääoma pienenee (luottotappio = jäljellä oleva lainapääoma).
- Likviditeettisääntö: jos oma pääoma / talletukset < pääomavaade → pankki siirtyy "stop lending" -tilaan, mikä muuttaa makrosykliä.

Rahamäärä ja mittarit (v0.3c)
- Money supply M1 = talletukset (pankkitalletukset ovat kotitalouksien käteinen) → kerätään DataCollectorilla.
- Muita mittareita: lainakanta, nettonostot (flow), default-aste, pankin pääomasuhde, korkokate, keskim. laina- ja talletuskorot.
- Lisää myös kotitalouksien taseisiin kentät `loan_balance` ja `debt_service_due` raportointia varten.

Työlista v0.3
1. Päivitä konfiguraatioon `banking`-lohko (korot, marginaalit, pääomavaatimus, stop-lending raja, default recovery).
2. Toteuta `agents/bank.py` jossa: taseen päivitys, lainapäätöksen logiikka, kuukausittainen velanhoito, tappioiden käsittely.
3. Kytke `BankAgent` `EconomyModel`-luokkaan: instanssi, referenssi kotitalouksiin/firmoihin, API-lisäykset household/firm steppeihin (lainahaku ja velanhoito ennen kulutusta/palkkoja).
4. Laajenna datankeruuta ja mittareita (M1, lainakanta, default rate, bank equity) + tulosta per step debug-yhteenveto `run_minimal.py`:ssa.
5. Kirjoita regressiotesti: aja 120 kk ja varmista, että ilman defaultteja talletukset ≈ lainat sekä korkokate näkyy pankin tuloksessa.

## **v0.4 – Dynaaminen Hyödykemarkkina ja Inflaatio** ⭐ KRIITTINEN
**Tavoite:** Kytkeä M1:n muutokset (v0.3) reaaliseen hintatasoon. Ilman tätä pankkijärjestelmä on merkityksetön.

### Miksi tämä on kriittinen?
- v0.3 teki rahan määrän dynaamiseksi (lainat luovat talletuksia).
- Ilman dynaamista hintatasoa M1-muutokset eivät vaikuta talouteen → malli on epätäydellinen.
- Asuntomarkkinan (v0.5) ja yrittäjyyden (v0.6) hinnoittelu vaatii toimivan inflaatiomekanismin.

### Mitä toteutetaan?
**FirmAgent-laajennukset:**
- Lisää varasto (`inventory`), hinta (`price`), tuotantofunktio (`produce()`)
- Hinnanasettelu-sääntö: jos varasto < tavoite → nosta hintaa (inflaatio); jos varasto > tavoite → laske hintaa (deflaatio)
- `sell_goods(units)` -metodi: myy tuotteita varastosta ja palauta myyntitulo

**HouseholdAgent-muutokset:**
- Korvaa `consume()`: sen sijaan että raha vain "katoaa", agentti ostaa hyödykkeitä yrityksiltä niiden asettamaan hintaan
- `units_to_buy = budget / firm.price` → osto tapahtuu agenttien välillä
- ALV maksetaan ostohetkellä valtiolle

**core/model.py-yksinkertaistus:**
- **POISTETAAN** vanha `total_consumption`-jako yrityksille
- Kulutus tapahtuu nyt suoraan agenttien välillä (household → firm)

**Uusi mittari:**
- **CPI (Consumer Price Index)** = yritysten hintojen keskiarvo
- Mahdollistaa inflaation/deflaation seurannan

### Työlista v0.4
1. Päivitä `agents/firm.py`: lisää `price`, `inventory`, `production_per_month`, `target_inventory`
2. Toteuta `FirmAgent._produce()`, `_update_price()` ja `sell_goods(units)`
3. Muokkaa `agents/household.py`: korvaa `consume()` ostamaan yrityksiltä
4. Yksinkertaista `core/model.py.step()`: poista vanha kulutuslogiikka
5. Lisää CPI-mittari DataCollectoriin
6. Testaa: tarkista että hinnat reagoivat kysyntään ja M1-muutoksiin

## **v0.5 – Asuntomarkkina ja Asuntolainat** 🏠
**Tavoite:** Mallintaa asuntomarkkinat realistisesti, jossa **kotitalouksien muodostuminen** (ei pelkkä väestömäärä) ajaa kysyntää. Syntyvyys, perhekoko ja yksineläjät vaikuttavat asuntojen tarpeeseen ja hintoihin.

### Kriittiset Oivallukset
1. **Asuntojen kysyntä ≠ väestömäärä**, vaan kotitalouksien määrä
2. **Syntyvyys vaikuttaa viiveellä**: Lapsi syntyy → 20v myöhemmin "pesästä lentäjä" → uusi asunnon tarve
3. **Perhekoko määrää asunnon koon**: 1 hlö → yksiö, 4 hlö → kolmio
4. **Hinnat segmentoituvat kokojen mukaan**: yksiöiden ja perheasuntojen markkinat ovat erilliset

### Toteutus

#### 1. Kotitalouden Koko -semantiikka
**Muokkaa `HouseholdAgent`:**
```python
# Uudet muuttujat
self.household_size: int = 1  # Montako henkilöä tässä kotitaloudessa
self.num_children: int = 0  # Lasten määrä
self.dwelling: Dwelling | None = None  # Viite asuntoon
```

**Muokkaa `process_births()`:**
- Lapsi EI ole erillinen agentti syntymästä
- Kasvattaa vanhemman `household_size += 1` ja `num_children += 1`
- Lapsi "aktivoituu" agentiksi vasta 18-25v iässä ("pesästä lentäminen")

**Lisää `check_leaving_home()`:**
- Nuoret muuttavat pois → `parent.household_size -= 1`
- Luodaan uusi `HouseholdAgent(age=20, household_size=1)` → **asunnon tarve**

#### 2. Dwelling (Asunto) -luokka
**Luo `markets/housing.py`:**
```python
class Dwelling:
    id: int
    size: int  # 1=yksiö, 2=kaksio, 3=kolmio, 4=neliö+
    base_value: float  # Perushinta (riippuu koosta)
    market_value: float  # Dynaaminen hinta
    owner: HouseholdAgent | None
    for_sale: bool
    construction_year: int  # Asunnon ikä
```

**Aloituskanta:**
- Luodaan jakauma: 30% yksiöitä, 30% kaksioita, 25% kolmioita, 15% neliöitä+
- Base_value suhde: 1.0x, 1.5x, 2.0x, 2.5x

#### 3. Asunnon Tarve ja Ostopäätös
**Lisää `HouseholdAgent`:**
```python
def needs_housing(self) -> bool:
    # Ei omista + työssä + aikuinen
    if self.dwelling is None and self.employed and self.age >= 20:
        return True
    # Omistaa, mutta perhe kasvanut liian isoksi
    if self.dwelling and self.household_size > self.dwelling.size * 1.5:
        return True  # Päivitystarve
    return False

def required_dwelling_size(self) -> int:
    if self.household_size == 1: return 1
    elif self.household_size == 2: return 2
    elif self.household_size <= 4: return 3
    else: return 4
```

#### 4. Markkinamekanismi
**Lisää `EconomyModel.step()`:**
```python
def housing_market_step(self):
    # 1. Päivitä hinnat kokojen mukaan segmentoituna
    for size in [1, 2, 3, 4]:
        buyers = [h for h in self.households if h.needs_housing() 
                  and h.required_dwelling_size() == size]
        sellers = [d for d in self.dwellings if d.for_sale and d.size == size]
        
        pressure = len(buyers) / max(1, len(sellers))
        
        # Hintamuutos = paikallinen kysyntä + CPI-linkitys
        local_change = 1.03 if pressure > 1.2 else (0.97 if pressure < 0.8 else 1.0)
        cpi_effect = (self.cpi / self.cpi_base - 1) * 0.5  # 50% CPI-sensit.
        
        for d in [dw for dw in self.dwellings if dw.size == size]:
            d.market_value *= (local_change + cpi_effect)
    
    # 2. Kaupankäynti
    self._execute_housing_transactions()
```

#### 5. Asuntolainat ja Pankki
**Laajenna `BankAgent.request_loan`:**
```python
def can_approve_mortgage(self, borrower, dwelling):
    # LTV: max 85%
    down_payment = dwelling.market_value * 0.20
    if borrower.cash < down_payment:
        return False
    
    loan = dwelling.market_value - down_payment
    ltv = loan / dwelling.market_value
    if ltv > 0.85:
        return False
    
    # LTI: max 4.5x vuositulot
    annual_income = borrower.expected_monthly_income() * 12
    if loan > annual_income * 4.5:
        return False
    
    # Stressitesti: korko + 2%, max 35% tuloista
    stressed_payment = self._payment(loan, self.rate + 0.02, 300)
    if stressed_payment > borrower.expected_monthly_income() * 0.35:
        return False
    
    return True
```

#### 6. Tarjonnan Dynamiikka
**Kierto (Turnover):**
- Kun agentti kuolee → `dwelling.for_sale = True`
- Perintö: Asunnon arvo siirtyy perillisille

**Uudisrakentaminen:**
```python
def consider_new_construction(self):
    # Jos hinnat yli rakennuskustannusten → rakennetaan lisää
    avg_price = sum(d.market_value for d in self.dwellings) / len(self.dwellings)
    if avg_price > self.construction_cost * 1.3:
        # Rakenna sitä kokoa, missä suurin kysyntäpaine
        size = self._most_demanded_size()
        new_dwelling = Dwelling(size=size, base_value=...)
        self.dwellings.append(new_dwelling)
```

### Mittarit (DataCollector)
```python
"avg_household_size": kotitalouden keskikoko
"residents_per_dwelling": asukasta per asunto (vastaa kysymykseesi!)
"housing_ownership_rate": omistusasumisen aste
"avg_house_price_size_1/2/3/4": hinnat kokojen mukaan
"house_price_to_income": hinta-tulo-suhde
"mortgage_debt_to_gdp": asuntolainat / BKT
"housing_transactions_per_month": kauppojen määrä
```

### Työlista v0.5
1. Lisää `household_size`, `num_children`, `dwelling` `HouseholdAgent`-luokkaan
2. Muokkaa `process_births()`: lapsi kasvattaa `household_size`, ei luo agenttia
3. Lisää `check_leaving_home()`: nuoret muuttavat pois → uusi agentti
4. Luo `markets/housing.py`: `Dwelling`-luokka ja `HousingMarket`
5. Toteuta `needs_housing()` ja `required_dwelling_size()`
6. Lisää `housing_market_step()` `EconomyModel.step()`:iin
7. Laajenna `BankAgent`: asuntolainojen hyväksyntälogiikka (LTV/LTI/stressitesti)
8. Lisää kaikki mittarit DataCollectoriin
9. Testaa: aja simulaatio syntyvyydellä 1.3 vs. 2.1 → katso `residents_per_dwelling`

### Odotetut Tulokset
- **Matala syntyvyys (1.3)** → Enemmän yksineläjiä → `residents_per_dwelling` ~1.4-1.6
- **Korkea syntyvyys (2.1)** → Isompia perheitä → `residents_per_dwelling` ~2.2-2.5
- **Yksiöiden hinnat nousevat** enemmän matalalla syntyvyydellä (kysyntä)
- **Perheasuntojen hinnat nousevat** enemmän korkealla syntyvyydellä

## **v0.6 – Yrittäjyys ja Konkurssit** 🏢
**Tavoite:** Sosiaalinen liikkuvuus ja pääoma-agentiksi nouseminen. Kotitalous voi perustaa yrityksen ja nousta yrittäjäksi.

### Yleinen Yrittäjyysmekaniikka (Ei vielä erikoistumista)

**HouseholdAgent voi perustaa FirmAgent:in:**
- Vaatimus: Tarpeeksi käteistä (siemenpääoma) + työssäolo + ikä 25-55v
- Todennäköisyys: Esim. 0.5% per kuukausi per kelvollinen kotitalous
- Pankki myöntää yrityslainan (korkeampi korko kuin kulutusluotolle)

**FirmAgent-laajennus:**
- `owner: HouseholdAgent | None` - Viite perustajaan (jos yrittäjäyritys)
- `equity: float` - Oma pääoma (varat - velat)
- Konkurssi: Jos `equity < 0` ja `cash < 0` → yritys poistuu

**Vaikutukset:**
- Työllisyys: Uusi yritys voi palkata työntekijöitä
- Tuloerot: Onnistuneet yrittäjät rikastuvat, epäonnistuneet köyhtyvät
- Pankki: Yrityslainat kasvattavat luottokantaa

### Työlista v0.6
1. Lisää `owner` ja `equity` `FirmAgent`:iin
2. Toteuta `HouseholdAgent.try_start_business()`
3. Lisää konkurssimekaniikka `FirmAgent.check_bankruptcy()`
4. Laajenna `BankAgent`: yrityslainojen riskiarvio
5. Mittarit: yrittäjyysaste, yritysten syntyvyys/kuolleisuus

---

## **v0.7 – Yritystyypit ja Rakennusliike** 🏗️ ⭐ KRIITTINEN
**Tavoite:** Mallinnetaan uusien asuntojen rakentaminen **taloudellisena prosessina**, ei maagisena spawnauksena. Rakentaminen luo työpaikkoja, kuluttaa materiaaleja ja vaatii rahoitusta.

### Miksi tämä on kriittinen?

**Nykyinen ongelma (v0.5):**
- Asunnot ilmestyvät tyhjästä ilman taloudellista vaikutusta
- Ei työllisyyttä, ei pääomakiertoa, ei suhdannesykliä

**Ratkaisu:**
- Rakentaminen on **investointiprosessi**, joka sitoo pääomaa ja työtä aikaan
- Rakennusliike on **erikoistunut** FirmAgent, joka:
  1. Analysoi markkinoita
  2. Hakee rahoitusta pankilta
  3. Palkkaa työtä ja ostaa materiaaleja
  4. Luo uuden asunnon 6-12kk kuluttua
  5. Myy sen ja laskee voiton

### Toteutus

#### 1. FirmAgent-erikoistuminen
**Lisää `firm_type` -kenttä:**
```python
self.firm_type: str = "manufacturer"  # tai "construction", "service"
```

**Rakennusliike-spesifiset kentät:**
```python
if self.firm_type == "construction":
    self.construction_projects: list[ConstructionProject] = []
    self.construction_cost_per_sqm: float = 2000.0
    self.construction_duration_months: int = 12
    self.target_profit_margin: float = 0.15  # 15%
    self.max_concurrent_projects: int = 3
```

#### 2. ConstructionProject -dataluokka
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
```

#### 3. 5-Vaiheinen Rakentamisprosessi

**Vaihe 1: Markkina-analyysi**
- Rakennusliike tarkkailee `housing_market.avg_price_for_size()`
- Jos `market_price > construction_cost * 1.15` → Kannattaa rakentaa

**Vaihe 2: Rahoitus**
- Hae rakennuslaina: `bank.request_loan(purpose="construction")`
- Laina siirtyy yrityksen kassaan

**Vaihe 3: Rakennusvaihe (12kk)**
Joka kuukausi projekti:
- **Palkkaa työtä:** Maksaa palkkoja työttömille → luo työpaikkoja
- **Ostaa materiaaleja:** Ostaa muilta yrityksiltä (v0.4 hyödykemarkkina) → kiihdyttää taloutta
- Kirjaa kulut `project.spent_so_far`:iin

**Vaihe 4: Valmistuminen**
- Luodaan uusi `Dwelling` → `housing_market.dwellings`
- Asetetaan heti myyntiin (`for_sale = True`)

**Vaihe 5: Myynti ja Tuloslaskelma**
- Kun asunto myydään: `revenue = dwelling.market_value`
- Voitto = `revenue - spent_so_far - lainakorot`
- Maksa laina pois pankille

#### 4. Integrointi

**EconomyModel.step():**
```python
for firm in self.firms:
    firm.step()
    if firm.firm_type == "construction":
        firm._progress_construction_projects()
        firm._consider_new_construction_project()
```

#### 5. Taloudelliset Vaikutukset

**Suhdannesykli:**
- Asuntojen hinnat nousevat (v0.5) → Rakentajat aktivoituvat (v0.7)
- Rakentaminen luo työpaikkoja → Tulot kasvavat → Kysyntä kasvaa
- Tarjonta kasvaa → Hinnat stabiloituvat tai laskevat
- Rakentaminen hidastuu → Työttömyys kasvaa → Sykli kääntyy

**Pankkisektori:**
- Rakennuslainat ovat iso osa luottokantaa
- Jos projektit epäonnistuvat → Pankin tappiot kasvavat

**Työllisyys:**
- Rakennussektori työllistää 5-10% työvoimasta
- Suhdanneherkkä: Nousussa palkkaa, laskussa irtisanoo

### Mittarit (v0.7)
```python
"construction_projects_active": Aktiivisten projektien määrä
"construction_employment": Rakennusalan työpaikat
"dwellings_completed_per_month": Valmistuneet asunnot
"construction_sector_cash": Rakennusliikkeiden kassatilanne
"avg_construction_profit_margin": Keskimääräinen voittomarginaali
```

### Työlista v0.7
1. Lisää `firm_type` `FirmAgent`:iin
2. Luo `ConstructionProject` -dataluokka
3. Toteuta 5-vaiheinen prosessi:
   - `_consider_new_construction_project()`
   - `_start_construction_project()`
   - `_progress_construction_projects()`
   - `_pay_construction_wages()` ja `_buy_construction_materials()`
   - `_complete_construction_project()`
4. Integroi `EconomyModel.step()`:iin
5. Poista vanha `consider_new_construction()` `HousingMarket`:sta
6. Lisää mittarit DataCollectoriin
7. Testaa: Aja simulaatio ja katso rakentamisen suhdannesykli

---

Verotus, tulonsiirrot ja politiikkasäännöt "oikeasti" (v0.8)
Tavoite: tehdä valtio-osasta realistisempi.

Progressiiviset tuloverotaulukot, pääomaverot, ALV:n kiinnitys hyödykemarkkinaan.
Tulonsiirrot: eläkkeet, työttömyys, minimiturva.
Valtion budjetti ja velka:
jos alijäämä → valtio ottaa lainaa (vähintään kirjanpidollisesti) pankilta.
Mittarit: valtion velka/BKT-proxy, alijäämä, nettotulonsiirrot tulodesiileittäin.

Makrotilastot ja validointityökalut (v0.9)
Tavoite: kunnollinen mittaripaketti analyysia varten.

io/metrics.py:
Gini (tulot, varallisuus), työttömyysaste, palkkataso, asuntoindeksi, luottokanta, M1, valtion alijäämä, **CPI/inflaatio**, **rakennusalan työpaikat**.
scripts/run_scenario.py:
aja simulaatio N kuukautta, tallenna mittarit CSV/Parquet-muotoon ja tee pari peruskuvaa (Gini vs. aika, asuntoindeksi vs. aika, inflaatio vs. aika, rakentamisen sykli).

LOB ja markkinamikrorakenne erillisenä moduulina (v0.10)
Tavoite: kytkeä mukaan pörssimarkkina, mutta vasta kun makrokerros on pystyssä.

markets/lob.py:
LOB-rakenne (hintatasot, määrä, FIFO).
Yksinkertainen "market maker + momentum trader" -kokoonpano.
Aikataajuus: aloita yhdellä "päivän sisäisellä" loopilla per kuukausi (esim. 100 micro-stepiä).
Mittarit: tuottojen jakauma, volatiliteetin klusteroituminen, spread.

Kalibrointi ja validointi (v1.0)

calibration/-moduuli, jossa:
Parametrien perussetti (FI-tyylinen): säästöaste, verot, korkotasot → kovakoodattuna tai yksinkertaisessa YAML/JSON-konfigissa.
SMM-tyylinen looppi: aja simulaatio, laske momentit, vertaile referenssilukuihin, tee karkea haku.
Herkkyys: yksinkertaiset grid-sweep-skenaariot (korko ylös/alas, verot ylös/alas, asuntomarkkinashokki).

---

## Yhteenveto Päivitetystä Roadmapista

**v0.1** – Perussykli ✓  
**v0.2** – Elinkaari ja taseet ✓  
**v0.3** – Pankit ja endogeeninen raha ✓  
**v0.4** – Dynaaminen hyödykemarkkina ja inflaatio ✓  
**v0.5** – Asuntomarkkina (kysyntä) ja asuntolainat ✓  
**v0.6** – Yrittäjyys ja konkurssit (yleinen mekaniikka)  
**v0.7** – **Yritystyypit ja Rakennusliike** ⭐ (SEURAAVA: KRIITTINEN)  
**v0.8** – Realistinen valtio  
**v0.9** – Kattava mittaripaketti  
**v0.10** – Rahoitusmarkkinat (LOB)  
**v1.0** – Kalibrointi ja validointi  

**Keskeiset muutokset:**
1. **v0.4** (Inflaatio) on nyt välittömästi v0.3:n jälkeen - M1-muutokset vaativat dynaamisen hintapinnan ✓
2. **v0.5** keskittyy asuntomarkkinan **kysyntään** (kotitalouksien muodostuminen, ostopäätökset) ✓
3. **v0.7** (UUSI VAIHE) keskittyy asuntomarkkinan **tarjontaan** (rakentaminen taloudellisena prosessina) ⭐
4. **Rakentaminen ei ole enää maagista** - se luo työpaikkoja, kuluttaa materiaaleja, vaatii rahoitusta ja ajaa suhdannesykliä

---

## Käytännön ensimmäiset konkreettiset askeleet tänään

Ehdotan, että aloitetaan aivan käytännöstä:

Luo hakemistorakenne core/, agents/, markets/, policy/, io/, scripts/ taloussimu -kansioon.
Teen sinulle luonnoksen seuraavista tiedostoista (voit pyytää ne yksitellen tai pakettina):
core/model.py: yksinkertainen EconomyModel + kuukausiaskel (Mesa-runko).
agents/household.py, agents/firm.py, agents/state.py, agents/bank.py (tyhjät rungot, v0.1-v0.3 mielessä).
scripts/run_minimal.py: aja 120 kuukautta ja tulosta pari mittaria.
Sen jälkeen ajetaan ensimmäinen superyksinkertainen simulaatio (ei pankkia, ei asuntoja) ja katsotaan, että looppi toimii.
Jos haluat, voin seuraavaksi ehdottaa tarkkaa Python-moduulirakennetta (tiedostojen nimet + luokkien nimet ja tärkeimmät metodit) ja sitten alkaa täyttää niistä ensimmäisen version (EconomyModel + HouseholdAgent + FirmAgent + StateAgent + ajoskripti).