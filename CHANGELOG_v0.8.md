# CHANGELOG v0.8: Realistinen valtio

**Toteutettu:** 2025-01-14

## Yhteenveto

v0.8 tuo simulaatioon realistisen valtion toiminnan progressiivisella verotuksella, yritysverotuksella, budjettiseurannalla ja julkisilla hankinnoilla. Vanha flat tax -järjestelmä korvattiin kattavalla fiskaalipolitiikan mallilla.

## Keskeiset muutokset

### 1. Progressiivinen tulovero

**Aiemmin (v0.7):**
- Tasavero 25% kaikille palkansaajille
- Ei ota huomioon tulotasoa

**Nyt (v0.8):**
- Progressiiviset veroluokat:
  - 0-15k €: 5%
  - 15k-30k €: 15%
  - 30k-50k €: 25%
  - 50k+ €: 35%
- Marginaalivero lasketaan oikein (vain ylimenevä osa)
- Konfiguroitavissa `config/base.yaml`:ssa

### 2. Yhteisövero (Corporate Tax)

**Uusi ominaisuus:**
- Vero yritysten voitoista (tulot - menot)
- 20% oletusverokanta
- Yritykset kirjaavat nyt kuukausittaiset tulot ja menot
- Vero kerätään vain positiivisista voitoista
- Kerätään ENNEN uuden kuukauden kirjanpidon nollaamista

**Tekninen toteutus:**
```python
# agents/firm.py
class FirmAgent:
    revenue_this_month: float = 0.0  # Uusi
    expenses_this_month: float = 0.0  # Uusi
    
    def pay_wages(self):
        self.expenses_this_month += wages  # Kirjaa meno
    
    def sell_goods(self, units):
        revenue = units * self.price
        self.revenue_this_month += revenue  # Kirjaa tulo
```

### 3. Kohdennetut tulonsiirrot

**Aiemmin:**
- Tulonsiirrot maksettiin kaikille kotitalouksille

**Nyt:**
- Työttömyystuki (1,200 €/kk): Vain työttömille
- Eläke (1,500 €/kk): Vain eläkeläisille (>65v)
- Työssäkäyvät eivät saa tulonsiirtoja

### 4. Budjettiseuranta ja velkamekanismi

**Uusi ominaisuus:**
- Kuukausittainen budjetin laskenta
- Automaattinen velan liikkeeseenlasku jos alijäämä
- Velanhoitokustannukset (3% vuodessa)
- Seurannat:
  - `monthly_revenue`: Kaikki tulot
  - `monthly_expenses`: Kaikki menot
  - `surplus`: Ylijäämä/alijäämä
  - `total_debt`: Valtion kokonaisvelka
  - `debt_to_gdp`: Velka suhteessa BKT:hen

**Järjestys:**
```python
# core/model.py step()
1. Yhteisövero (edellisen kk voitoista)
2. Firmat step (tuotanto, palkanmaksu)
3. Velanhoito
4. Tulonsiirrot
5. Tulovero
6. Julkiset hankinnat
7. Kotitaloudet kuluttavat (ALV)
8. Budjetti ja velkasaldo
```

### 5. Julkiset hankinnat

**Uusi ominaisuus:**
- Valtio ostaa hyödykkeitä manufacturer-yrityksiltä
- Osuus: 15% edellisen kuukauden kassasaldosta
- Tuki yritysten kysynnälle
- Simuloi julkisia palveluja (terveydenhuolto, koulutus, infrastruktuuri)

### 6. Pääomatulovero (Capital Gains Tax)

**Uusi ominaisuus:**
- 30% vero asuntojen myyntivoitoista
- Lasketaan: `myyntihinta - rakennuskustannus`
- Kerätään vain jos voittoa syntyy
- Rakennusyritykset tallentavat `construction_cost` asuntoihin

**Tekninen toteutus:**
```python
# markets/housing.py
if sale_price > old_dwelling.construction_cost:
    capital_gain = sale_price - old_dwelling.construction_cost
    self.model.state.collect_capital_gains_tax(buyer, capital_gain)
```

## Uudet metriikat

Lisätty 13 uutta valtion metriikkaa `DataCollector`:iin:

**Tulot:**
- `state_monthly_revenue`: Kokonaistulot
- `state_income_tax`: Tulovero
- `state_corporate_tax`: Yhteisövero
- `state_vat`: ALV
- `state_capital_gains_tax`: Myyntivoittovero

**Menot:**
- `state_monthly_expenses`: Kokonaismenot
- `state_transfers`: Tulonsiirrot
- `state_debt_service`: Velanhoito
- `state_public_procurement`: Julkiset hankinnat

**Budjetti:**
- `state_surplus`: Ylijäämä/alijäämä
- `state_total_debt`: Kokonaisvelka
- `state_debt_to_gdp`: Velka/BKT
- `effective_tax_rate`: Efektiivinen veroprosentti

## Tekninen arkkitehtuuri

### StateAgent (agents/state.py)

**Uudelleenkirjoitettu kokonaan:**

```python
class StateAgent:
    # Tase
    cash_balance: float
    total_debt: float
    
    # Kuukausittaiset
    monthly_revenue: float
    monthly_expenses: float
    
    # Tulojen erittely
    income_tax_revenue: float
    corporate_tax_revenue: float
    vat_revenue: float
    capital_gains_revenue: float
    
    # Menojen erittely
    transfer_expenses: float
    debt_service_expenses: float
    public_procurement_expenses: float
    
    # Parametrit
    income_tax_brackets: list[tuple[float, float, float]]
    corporate_tax_rate: float
    vat_rate: float
    capital_gains_rate: float
    debt_interest_rate_annual: float
    public_spending_share: float
```

**Metodit:**
- `reset_monthly_counters()`: Nollaa kuukausittaiset laskurit
- `collect_income_tax()`: Progressiivinen tulovero
- `collect_corporate_tax()`: Yritysvero
- `collect_vat(amount)`: ALV (passiivinen)
- `collect_capital_gains_tax(hh, gain)`: Myyntivoittovero
- `pay_transfers()`: Kohdennetut tulonsiirrot
- `pay_debt_interest()`: Velanhoito
- `make_public_purchases()`: Julkiset hankinnat
- `run_budget()`: Budjetin laskenta ja velka
- `_calculate_progressive_tax(income)`: Progressiivisen veron laskenta

### Konfiguraatio (config/base.yaml)

**Lisätty:**
```yaml
taxes:
  # Progressiivinen tulovero
  income_brackets:
    - [0, 15000, 0.05]
    - [15000, 30000, 0.15]
    - [30000, 50000, 0.25]
    - [50000, 999999, 0.35]
  
  corporate_tax_rate: 0.20
  vat_rate: 0.24
  capital_gains_rate: 0.30

state:
  debt_interest_rate_annual: 0.03
  public_spending_share: 0.15
```

**Poistettu:**
```yaml
taxes:
  income_flat_rate: 0.25  # ← Vanha flat tax
```

## Suorituskyky ja tulokset

**120 kuukauden simulaatio:**
- Työttömyys: ~32.7% (kohtuullinen)
- Valtion ylijäämä: +10,243 €/kk
- Valtion velka: 2,123,370 € (71.5% BKT:stä)
- Efektiivinen veroprosentti: 44.6%
- Verotulot:
  - Tulovero: 7.2%
  - Yhteisövero: 22.1%
  - ALV: 70.7%
- Julkiset hankinnat: 58,965 €/kk

**Verrokkina v0.7:**
- Työttömyys: ~31.4%
- Valtion ylijäämä: +106,259 €/kk (liian suuri)
- Ei velkaa
- Ei julkisia hankintoja

## Tulevat parannukset (PLAN_v0.8.md Phase 3)

**Suunniteltu mutta ei vielä toteutettu:**
1. Varallisuusvero (Wealth Tax)
2. Infrastruktuurirahasto tuottavuushyödyillä
3. Valtionlainat yksityisille
4. Suhdannevastainen politiikka

## Bugit korjattu

1. **Yhteisöveron ajoitus:**
   - Ongelma: Yhteisövero kerättiin JÄLKEEN firmojen kirjanpidon nollauksen
   - Ratkaisu: Siirretty ennen firmojen steppiä

2. **Julkisten hankintojen inventory:**
   - Ongelma: Julkiset hankinnat eivät löytäneet ostettavaa (inventory tyhjä)
   - Ratkaisu: Siirretty ennen kotitalouksien kulutusta

3. **Konfiguraation avaimet:**
   - `corporate_rate` → `corporate_tax_rate`
   - `debt_interest_rate` → `debt_interest_rate_annual`

4. **Progressiivisen veron laskenta:**
   - Varmistettu että marginaalivero lasketaan oikein (vain ylimenevä osa)

## Yhteensopivuus

- ✅ Yhteensopiva v0.7:n kanssa (firm_type, construction projects)
- ✅ Yhteensopiva v0.6:n kanssa (entrepreneurship)
- ✅ Yhteensopiva v0.5:n kanssa (housing market)
- ✅ Backward compatible config (oletusarvot jos puuttuu)

## Testaus

**Suoritettu:**
- 120 kuukauden simulaatio
- Progressiivisen veron laskenta (2,500 €/kk palkka → 250 €/kk vero)
- Yhteisöveron keräys yritysten voitoista
- Julkisten hankintojen jako manufacturer-yrityksille
- Budjettialijäämän velkaanto

**Tulos:** ✅ Kaikki toimii suunnitellusti
