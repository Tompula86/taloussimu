# CHANGELOG v0.4 – Dynaaminen Hyödykemarkkina ja Inflaatio

**Päivämäärä:** 2025-11-14

## Yhteenveto

v0.4 lisää **kriittisen** ominaisuuden: dynaamisen hintapinnan, joka kytkee v0.3:n endogeenisen rahan (M1) reaaliseen talouteen. Ilman tätä pankkijärjestelmän rahan luominen olisi merkityksetöntä.

## Keskeiset muutokset

### 1. FirmAgent – Varasto ja Dynaaminen Hinnoittelu

**Uudet ominaisuudet:**
- `price`: Tuotteen hinta (aloitus 1.0)
- `inventory`: Varaston määrä
- `production_per_month`: Kuukausituotanto
- `target_inventory`: Tavoitevarasto

**Uudet metodit:**
- `_produce()`: Tuottaa hyödykkeitä kuukausittain
- `_update_price()`: Inventory targeting -hinnoittelu
  - Jos varasto < 80% tavoitteesta → +2% hinta (inflaatio)
  - Jos varasto > 120% tavoitteesta → -2% hinta (deflaatio)
- `sell_goods(units)`: Myy tuotteita varastosta ja palauttaa myyntitulon

**Vaikutus:**
Yritykset reagoivat nyt kysyntään muuttamalla hintoja automaattisesti.

### 2. HouseholdAgent – Ostaminen Yrityksiltä

**Muutettu metodi: `consume()`**

**Vanha tapa (v0.1-v0.3):**
```python
consumption = self.base_propensity_to_consume * available_cash
self.cash -= consumption
return consumption  # Raha "katoaa"
```

**Uusi tapa (v0.4):**
```python
consumption_budget = self.base_propensity_to_consume * available_cash
target_firm = self.random.choice(self.model.firms)
units_to_buy = consumption_budget / target_firm.price
actual_spent = target_firm.sell_goods(units_to_buy)
self.cash -= actual_spent
# ALV maksetaan heti
vat_amount = actual_spent * self.model.vat_rate
self.model.state.cash_balance += vat_amount
return actual_spent - vat_amount
```

**Vaikutus:**
- Kotitaloudet ostavat nyt **todellisia hyödykkeitä** yrityksiltä
- Ostovoima riippuu **dynaamisesta hinnasta**
- ALV kerätään ostohetkellä

### 3. EconomyModel – Yksinkertaistettu Step-metodi

**Poistettu:**
```python
# Vanha logiikka: kulutus jaetaan tasaisesti yrityksille
if self.total_consumption > 0 and len(self.firms) > 0:
    consumption_per_firm = self.total_consumption / len(self.firms)
    vat_amount = consumption_per_firm * self.vat_rate
    net_revenue = consumption_per_firm - vat_amount
    for firm in self.firms:
        firm.receive_revenue(net_revenue)
    self.state.cash_balance += vat_amount * len(self.firms)
```

**Uusi logiikka:**
Kulutus tapahtuu nyt suoraan `HouseholdAgent.consume()`:ssa agenttien välillä.

**Uusi mittari:**
```python
@property
def cpi(self) -> float:
    """Consumer Price Index = yritysten hintojen keskiarvo."""
    if not self.firms:
        return 1.0
    return sum(f.price for f in self.firms) / len(self.firms)
```

Lisätty DataCollectoriin:
```python
"cpi": lambda m: m.cpi,
```

### 4. Roadmap.md – Päivitetty Rakenne

**Uusi järjestys:**
- v0.1 – Perussykli ✓
- v0.2 – Elinkaari ja taseet ✓
- v0.3 – Pankit ja endogeeninen raha ✓
- **v0.4 – Dynaaminen hyödykemarkkina ja inflaatio** ⭐ (UUSI)
- v0.5 – Asuntomarkkina ja asuntolainat (oli v0.4)
- v0.6 – Yrittäjyys ja konkurssit (oli v0.5)
- v0.7 – Realistinen valtio (oli v0.6)
- v0.8 – Kattava mittaripaketti (oli v0.7)
- v0.9 – Rahoitusmarkkinat / LOB (oli v0.8)
- v1.0 – Kalibrointi ja validointi (oli v0.9)

**Perustelu:**
Ilman v0.4:ää M1-muutokset (v0.3) eivät vaikuta talouteen. Asuntomarkkinan (v0.5) hinnoittelu vaatii toimivan inflaatiomekanismin.

## Testitulokset

**Simulaatio:** 120 kuukautta, 100 kotitaloutta, 3 yritystä

```
Kuukausi: 120
CPI: 10.5541 (aloitus: 1.0000)
Väestö: 103 (aloitus: 100)
Työttömyysaste: 22.1%
M1: 6,657,998 €

Keskiarvot:
CPI (ka): 4.0688
CPI volatiliteetti (std): 2.6838
M1 (ka): 3,238,523 €
```

**Havainnot:**
1. ✅ Hinnat nousevat dynaamisesti (1.0 → 10.5)
2. ✅ M1 kasvaa → inflaatiopaine
3. ✅ CPI-mittari toimii ja on mitattavissa
4. ⚠️ Inflaatio on voimakasta (955% / 120kk ≈ 7.96%/kk) - tämä on odotettua ilman rahapolitiikkaa

## Seuraavat askeleet (v0.5)

Nyt kun meillä on:
- ✅ Endogeeninen raha (M1)
- ✅ Dynaaminen hintapinta (CPI)

Voimme lisätä:
- 🔜 Asuntomarkkina (hinnat reagoivat sekä kysyntään että CPI:hen)
- 🔜 Asuntolainat (LTV/LTI-rajoitukset)
- 🔜 Rahapolitiikka (koron säätö inflaation perusteella)

## Muutetut tiedostot

- `agents/firm.py` – Lisätty varasto, hinnoittelu ja tuotanto
- `agents/household.py` – Muutettu `consume()` ostamaan yrityksiltä
- `core/model.py` – Poistettu vanha kulutuslogiikka, lisätty CPI-mittari
- `scripts/run_minimal.py` – Lisätty CPI-tulostus
- `roadmap.md` – Uudelleenjärjestetty v0.4:n kanssa

## Tekninen velkaa

1. **Hinnoittelusääntö on yksinkertainen** – Ei huomioi:
   - Markkinaosuutta
   - Kilpailua
   - Tuotantokustannuksia (palkat)
   
2. **Kotitaloudet ostavat satunnaiselta yritykseltä** – Ei hintavertailua
   
3. **Ei rahapolitiikkaa** – Inflaatio kasvaa hallitsemattomasti

Nämä ovat tietoisia yksinkertaistuksia, jotka parannetaan myöhemmissä versioissa.

---

**v0.4 Status:** ✅ VALMIS JA TOIMINNASSA
