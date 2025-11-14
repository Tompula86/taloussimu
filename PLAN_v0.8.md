# V0.8 SUUNNITELMA: Realistinen Valtio

## Päivämäärä: 14.11.2025

## Tavoite
Tehdä valtio-osasta realistinen taloudellinen toimija, joka:
1. Kerää progressiivisia veroja (tulo-, yritys-, kulutus-, pääomaverot)
2. Maksaa kohdennettuja tulonsiirtojaä (työttömyys, eläke, perustulo)
3. Seuraa budjettia ja velkaa
4. Vaikuttaa talouteen dynaamisesti
5. Voi tehdä julkisia hankintoja

## Nykyiset Ongelmat (v0.7)

❌ **Tasavero kaikille** - Ei progressiivisuutta
❌ **Väärin laskettu veropohja** - Käyttää `firms[0].wage_level` kaikkien palkkoja varten
❌ **Ei yritysvero** - Yritykset eivät maksa veroa voitoistaan
❌ **Ei kohdennettuja tukia** - Kaikki saavat saman "työttömyystuen"
❌ **Ei budjettiseurantaa** - Vain `cash_balance`, ei tuloja/menoja erikseen
❌ **Ei velkamekanismia** - Jos saldo negatiivinen, ei tapahdu mitään
❌ **ALV epäselvä** - Household.consume() päivittää `state.cash_balance` suoraan

## Ratkaisut ja Ominaisuudet

### 1. TULOT (Revenue) - Monipuolinen verotus

#### A. Progressiivinen Tulovero
```python
INCOME_TAX_BRACKETS = [
    (0, 15000, 0.05),      # 0-15k€/v: 5%
    (15000, 30000, 0.15),  # 15-30k€/v: 15%
    (30000, 50000, 0.25),  # 30-50k€/v: 25%
    (50000, inf, 0.35)     # 50k+€/v: 35%
]
```
- Perustuu kotitalouden **todelliseen palkkaan** (`hh.wage`)
- Lasketaan vuositulojen perusteella, veloitetaan kuukausittain
- Maksetaan vain jos `hh.employed == True`

#### B. Yritysvero (Corporate Tax)
```python
corporate_tax_rate = 0.20  # 20%
```
- Verotetaan yrityksen **voittoa** (Revenue - Expenses)
- Tarvitsee kirjanpidon: `firm.revenue_this_month`, `firm.expenses_this_month`
- Maksetaan kuukauden lopussa

#### C. Arvonlisävero (VAT)
```python
vat_rate = 0.24  # 24%
```
- Kerätään ostohetkellä: `state.collect_vat(amount)`
- Kutsutaan `HouseholdAgent.consume()`:ssa
- Siisti rajapinta, ei suoraa `cash_balance` -muokkausta

#### D. Pääomatulovero (Capital Gains Tax) 🆕
```python
capital_gains_tax_rate = 0.30  # 30%
```
- Verotetaan asuntojen myyntivoittoa
- Kun `HouseholdAgent` myy asunnon: `profit = sale_price - purchase_price`
- Kutsutaan: `state.collect_capital_gains_tax(hh, profit)`

#### E. Varallisuusvero (Wealth Tax) 🆕
```python
wealth_tax_rate = 0.001  # 0.1% per vuosi
wealth_tax_threshold = 500000  # Vain jos net_worth > 500k€
```
- Kerätään kerran vuodessa (month % 12 == 0)
- Vain kotitalouksille, joiden `net_worth > threshold`

### 2. MENOT (Expenses) - Kohdennetut Tulonsiirrot

#### A. Työttömyystuki
```python
unemployment_benefit = 1200€  # per kuukausi
```
- Maksetaan VAIN jos:
  - `hh.alive == True`
  - `hh.employed == False`
  - `hh.age < retirement_age`
- Ei eläkeläisille, ei työssäkäyville

#### B. Eläkkeet
```python
pension_base = 1500€  # per kuukausi
```
- Maksetaan VAIN jos:
  - `hh.alive == True`
  - `hh.age >= retirement_age`
- Progressiivinen: `pension = pension_base * (hh.work_years / 40)` 🆕

#### C. Perustulo (Universal Basic Income) 🆕 [Valinnainen]
```python
basic_income = 500€  # per kuukausi
basic_income_enabled = False  # Konfiguraatiosta
```
- Maksetaan KAIKILLE elossa oleville
- Korvaa työttömyystuen ja eläkkeen (tai lisä niihin)
- Vertailukokeet: `basic_income_enabled = True/False`

#### D. Velanhoitokulut (Debt Service)
```python
debt_interest_rate_annual = 0.03  # 3% per vuosi
```
- Maksetaan korko olemassa olevalle velalle
- `monthly_interest = total_debt * (interest_rate / 12)`
- Itseään ruokkiva kierre: velka → korot → alijäämä → lisää velkaa

#### E. Julkiset Hankinnat (Public Procurement) 🆕
```python
public_spending_share = 0.15  # 15% tuloista
```
- Valtio ostaa hyödykkeitä yrityksiltä
- Simuloi: terveydenhuolto, koulutus, infrastruktuuri
- Palauttaa rahaa kiertoon
- Nostaa yritysten kysyntää

### 3. BUDJETTI JA VELKA (Budget & Debt)

#### A. Kirjanpito
```python
self.monthly_revenue: float = 0.0   # Tämän kuun tulot
self.monthly_expenses: float = 0.0  # Tämän kuun menot
self.cash_balance: float = 0.0      # Kassan tila
self.total_debt: float = 0.0        # Kumulatiivinen velka
```

#### B. Budjettilaskenta (Kuukauden lopussa)
```python
def _run_budget(self):
    surplus = self.monthly_revenue - self.monthly_expenses
    self.cash_balance += surplus
    
    # Jos kassa negatiivinen → ota velkaa
    if self.cash_balance < 0:
        needed_loan = -self.cash_balance
        self.total_debt += needed_loan
        self.cash_balance = 0.0
```

#### C. Velkakirjat (Government Bonds) 🆕 [v0.9]
- Sen sijaan että velka "syntyy tyhjästä"
- Valtio laskee liikkeelle obligaatioita
- `BankAgent` tai varakkaat `HouseholdAgent`-agentit voivat ostaa
- Velanhoitokulut siirtyvät tuloiksi haltijoille

### 4. INFRASTRUKTUURI JA JULKISET HYÖDYKKEET 🆕

#### A. Infrastruktuuri-rahasto
```python
infrastructure_investment_share = 0.10  # 10% tuloista
```
- Kasaantuu rahastoon: `self.infrastructure_stock`
- Vaikuttaa kaikkien yritysten tuottavuuteen:
  ```python
  productivity_multiplier = 1.0 + (infrastructure_stock / 1_000_000) * 0.1
  firm.production_per_employee *= productivity_multiplier
  ```
- Pitkän aikavälin vaikutus: parempi infra → korkeampi tuottavuus

#### B. Koulutusinvestoinnit
```python
education_spending_share = 0.05  # 5% tuloista
```
- Nostaa syntyvien lasten `skills`-parametria (v0.9+)
- Parempi koulutus → korkeammat palkat → korkeammat verotulot

### 5. DYNAAMINEN POLITIIKKA 🆕

#### A. Vastasuhdanne-politiikka (Counter-cyclical)
```python
def adjust_policy_to_cycle(self):
    unemployment = self.model.unemployment_rate
    
    if unemployment > 0.15:  # Lama: 15%+ työttömyys
        # Lisää menoja
        self.unemployment_benefit *= 1.05
        self.public_spending_share += 0.02
        # Tai laske veroja
        # self.income_tax_multiplier *= 0.95
    
    elif unemployment < 0.05:  # Ylikuumeneminen
        # Vähennä menoja
        self.public_spending_share -= 0.01
        # Tai nosta veroja
        # self.income_tax_multiplier *= 1.02
```

#### B. Velkakatto (Debt Ceiling)
```python
debt_to_gdp_max = 0.90  # 90%
```
- Jos `debt / gdp_proxy > threshold`:
  - Pakkosivu: leikkaa menoja 10%
  - Tai nosta veroja

## Toteutusjärjestys

### Vaihe 1: Perusteet (Tässä sessiossa)
1. ✅ Progressiivinen tulovero
2. ✅ Yritysvero
3. ✅ Kohdennetut tulonsiirrot (työttömyys, eläke)
4. ✅ Budjetti- ja velkaseuranta
5. ✅ Puhdas ALV-rajapinta

### Vaihe 2: Lisäominaisuudet (Tässä sessiossa)
6. ✅ Pääomatulovero (asuntojen myyntivoitot)
7. ✅ Julkiset hankinnat
8. ✅ Velanhoitokulut

### Vaihe 3: Edistyneet (v0.9+)
9. ⏳ Varallisuusvero
10. ⏳ Infrastruktuuri-rahasto
11. ⏳ Velkakirjat (bonds)
12. ⏳ Vastasuhdanne-politiikka

## Integraatio

### agents/state.py
- Täysin uusi toteutus
- Selkeät metodit jokaiselle verolle
- Budjettilaskenta `_run_budget()`

### core/model.py
- Muokkaa `step()`-järjestystä:
  1. Työmarkkinat (_run_labor_market)
  2. Yritykset maksavat palkat (firm.pay_wages)
  3. Valtio maksaa tulonsiirrot (state.pay_transfers)
  4. Valtio kerää tuloverot (state.collect_income_tax)
  5. Valtio kerää yritysverot (state.collect_corporate_tax)
  6. Kotitaloudet kuluttavat (hh.consume → ALV)
  7. Valtio laskee budjetin (state._run_budget)

### agents/firm.py
- Lisää kirjanpito:
  ```python
  self.revenue_this_month: float = 0.0
  self.expenses_this_month: float = 0.0
  ```
- Päivitä `pay_wages()`, `sell_goods()`, etc.

### agents/household.py
- Muokkaa `consume()` käyttämään `state.collect_vat()`
- Lisää `pay_capital_gains_tax()` asunnon myynnissä

### config/base.yaml
- Lisää `taxes:`-lohko:
  ```yaml
  taxes:
    income_brackets:
      - [0, 15000, 0.05]
      - [15000, 30000, 0.15]
      - [30000, 50000, 0.25]
      - [50000, .inf, 0.35]
    corporate_rate: 0.20
    vat_rate: 0.24
    capital_gains_rate: 0.30
    wealth_rate: 0.001
    wealth_threshold: 500000
  
  state:
    debt_interest_rate: 0.03
    public_spending_share: 0.15
    infrastructure_share: 0.10
  ```

## Mittarit (DataCollector)

### Uudet mittarit v0.8:
```python
"state_monthly_revenue": Kuukauden tulot
"state_monthly_expenses": Kuukauden menot
"state_surplus": Ylijäämä/alijäämä
"state_total_debt": Valtion velka
"state_debt_to_gdp": Velka/BKT-suhde
"state_income_tax_revenue": Tuloverotulot
"state_corporate_tax_revenue": Yritysverotulot
"state_vat_revenue": ALV-tulot
"state_capital_gains_revenue": Pääomaverotu lot
"state_transfer_expenses": Tulonsiirrot yhteensä
"state_debt_service": Velanhoitokulut
"effective_tax_rate": Todellinen veroaste (tulot/BKT)
```

## Odotetut Tulokset

### Realismi:
- Progressiivinen vero tasoittaa tulonjakoa (Gini laskee)
- Yritysvero tasapainottaa budjettia
- Velkakierre syntyy, jos alijäämä jatkuu

### Suhdanteet:
- Lama → alijäämä kasvaa (vähemmän veroja, enemmän tukia)
- Noususuhdanne → ylijäämä kasvaa (enemmän veroja, vähemmän tukia)

### Politiikkakoet:
- Vertaile: korkeat verot vs. matalat verot
- Vertaile: perus tulo vs. kohdistetut tuet
- Vertaile: julkiset hankinnat vs. ei hankintoja

---

**SEURAAVA TOIMENPIDE:** Aloita toteutus Vaihe 1 + Vaihe 2 ominaisuuksilla!
