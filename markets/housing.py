"""Asuntomarkkina v0.5.

Mallintaa asuntojen kysyntää, tarjontaa ja hinnanmuodostusta.
Kotitalouksien muodostuminen (ei pelkkä väestömäärä) ajaa kysyntää.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from agents.household import HouseholdAgent


class Dwelling:
    """Asunto-objekti.
    
    Ominaisuudet:
    - size: 1=yksiö, 2=kaksio, 3=kolmio, 4=neliö+
    - market_value: dynaaminen hinta (reagoi kysyntään ja CPI:hen)
    - owner: viite kotitalouteen joka omistaa asunnon
    - for_sale: onko myynnissä
    """
    
    def __init__(
        self,
        dwelling_id: int,
        size: int,
        base_value: float,
        construction_year: int = 0,
    ):
        self.id = dwelling_id
        self.size = size  # 1=yksiö, 2=kaksio, 3=kolmio, 4=neliö+
        self.base_value = base_value
        self.market_value = base_value  # Dynaaminen hinta
        self.owner: HouseholdAgent | None = None
        self.for_sale = True
        self.construction_year = construction_year
        self.location_multiplier = 1.0  # Tulevaisuus: sijainti
    
    def __repr__(self) -> str:
        owner_id = self.owner.unique_id if self.owner else None
        return (
            f"Dwelling(id={self.id}, size={self.size}, "
            f"value={self.market_value:.0f}, owner={owner_id}, "
            f"for_sale={self.for_sale})"
        )


class HousingMarket:
    """Asuntomarkkinan koordinaattori.
    
    Hoitaa:
    - Hinnoittelu kokojen mukaan segmentoituna
    - Kaupankäynti (transaktiot)
    - Uudisrakentaminen
    - Kierron seuranta
    """
    
    def __init__(self, model):
        self.model = model
        self.dwellings: list[Dwelling] = []
        self.next_id = 0
        self.construction_cost_base = 100000.0  # Perushinta uudisrakentamiselle
        self.monthly_transactions = 0
    
    def initialize_housing_stock(
        self,
        total_dwellings: int,
        distribution: dict[int, float] | None = None,
    ) -> None:
        """Luo alkuperäinen asuntokanta.
        
        Args:
            total_dwellings: Asuntojen kokonaismäärä
            distribution: Jakauma kokojen mukaan {size: osuus}
                         Default: {1: 0.30, 2: 0.30, 3: 0.25, 4: 0.15}
        """
        if distribution is None:
            distribution = {1: 0.30, 2: 0.30, 3: 0.25, 4: 0.15}
        
        # Base value -kertoimet (yksiö=1.0x, kaksio=1.5x, kolmio=2.0x, neliö+=2.5x)
        base_value_multipliers = {1: 1.0, 2: 1.5, 3: 2.0, 4: 2.5}
        
        for size, share in distribution.items():
            count = int(total_dwellings * share)
            for _ in range(count):
                base_value = self.construction_cost_base * base_value_multipliers[size]
                dwelling = Dwelling(
                    dwelling_id=self.next_id,
                    size=size,
                    base_value=base_value,
                    construction_year=0,
                )
                self.dwellings.append(dwelling)
                self.next_id += 1
    
    def update_prices(self) -> None:
        """Päivitä asuntojen hinnat segmentoituna kokojen mukaan.
        
        Hinnat reagoivat:
        1. Paikalliseen kysyntä-tarjonta-suhteeseen (size-spesifi)
        2. Yleiseen inflaatioon (CPI)
        """
        self.monthly_transactions = 0
        
        for size in [1, 2, 3, 4]:
            # Kokokohtainen kysyntä ja tarjonta
            size_dwellings = [d for d in self.dwellings if d.size == size]
            if not size_dwellings:
                continue
            
            buyers = [
                h for h in self.model.households
                if h.alive and h.needs_housing() and h.required_dwelling_size() == size
            ]
            sellers = [d for d in size_dwellings if d.for_sale]
            
            if not sellers:
                continue
            
            # Kysyntäpaine
            pressure = len(buyers) / len(sellers)
            
            # Paikallinen hintamuutos
            local_change = 1.0
            if pressure > 1.2:  # Kova kysyntä
                local_change = 1.03
            elif pressure < 0.8:  # Heikko kysyntä
                local_change = 0.97
            
            # CPI-linkitys (v0.4): Seuraa inflaatiomuutosta, ei kumulatiivista tasoa
            # Lasketaan kuukausittainen CPI-muutos, ei kokonaista muutosta alkuun
            current_cpi = self.model.cpi
            last_cpi = getattr(self.model, 'last_cpi', 1.0)
            cpi_monthly_change = current_cpi / max(last_cpi, 0.01) if last_cpi > 0 else 1.0
            # Rajoita CPI-vaikutus järkevälle tasolle (max ±10% per kuukausi)
            cpi_monthly_change = max(0.9, min(1.1, cpi_monthly_change))
            cpi_effect = (cpi_monthly_change - 1.0) * 0.3  # 30% sensitiivisyys
            
            # Yhdistetty muutos
            total_change = local_change + cpi_effect
            
            # Päivitä hinnat
            for dwelling in size_dwellings:
                dwelling.market_value *= total_change
    
    def execute_transactions(self) -> int:
        """Suorita asuntokaupat.
        
        Returns:
            Onnistuneiden kauppojen määrä
        """
        transactions = 0
        
        # Kerää ostajat ja myyjät
        potential_buyers = [
            h for h in self.model.households
            if h.alive and h.needs_housing()
        ]
        
        # Sekoita ostajat satunnaisessa järjestyksessä
        self.model.random.shuffle(potential_buyers)
        
        for buyer in potential_buyers:
            required_size = buyer.required_dwelling_size()
            
            # Etsi sopiva asunto
            available = [
                d for d in self.dwellings
                if d.for_sale and d.size == required_size
            ]
            
            if not available:
                continue
            
            # Valitse halvin
            dwelling = min(available, key=lambda d: d.market_value)
            
            # Yritä ostaa
            if self._try_purchase(buyer, dwelling):
                transactions += 1
                self.monthly_transactions += 1
        
        return transactions
    
    def _try_purchase(
        self,
        buyer: HouseholdAgent,
        dwelling: Dwelling,
    ) -> bool:
        """Yritä suorittaa asuntokauppa.
        
        Args:
            buyer: Ostaja
            dwelling: Asunto
            
        Returns:
            True jos kauppa onnistui
        """
        # 1. Tarkista käsiraha (20%)
        down_payment = dwelling.market_value * 0.20
        if buyer.cash < down_payment:
            return False
        
        # 2. Laske tarvittava laina
        loan_amount = dwelling.market_value - down_payment
        
        # 3. Pyydä asuntolainaa pankilta
        bank = getattr(self.model, 'bank', None)
        if bank is None:
            return False
        
        # Käytä pankin asuntolainalogiikkaa
        approved = bank.request_loan(
            borrower=buyer,
            amount=loan_amount,
            borrower_type="household",
            term_months=300,  # 25 vuotta
            purpose="mortgage",
        )
        
        if not approved:
            return False
        
        # 4. Kauppa menee läpi
        buyer.cash -= down_payment
        
        # Jos ostaja myi vanhan asunnon
        if buyer.dwelling is not None:
            old_dwelling = buyer.dwelling
            buyer.cash += old_dwelling.market_value  # Myyntitulo
            old_dwelling.owner = None
            old_dwelling.for_sale = True
        
        # Uusi omistus
        dwelling.owner = buyer
        dwelling.for_sale = False
        buyer.dwelling = dwelling
        
        return True
    
    def consider_new_construction(self) -> None:
        """Rakenna uusia asuntoja, jos hinnat ovat korkeat.
        
        Simuloi rakennusyhtiöitä, jotka reagoivat hintasignaaleihin.
        """
        if not self.dwellings:
            return
        
        # Keskihinta vs. rakennuskustannus
        avg_price = sum(d.market_value for d in self.dwellings) / len(self.dwellings)
        
        # Jos hinnat > 1.3x rakennuskustannus → kannattaa rakentaa
        if avg_price < self.construction_cost_base * 1.3:
            return
        
        # Rakenna sitä kokoa, missä suurin kysyntäpaine
        size_pressures = {}
        for size in [1, 2, 3, 4]:
            buyers = [
                h for h in self.model.households
                if h.alive and h.needs_housing() and h.required_dwelling_size() == size
            ]
            sellers = [d for d in self.dwellings if d.for_sale and d.size == size]
            pressure = len(buyers) / max(1, len(sellers))
            size_pressures[size] = pressure
        
        # Rakenna eniten kysyttyä kokoa
        most_demanded_size: int = max(size_pressures, key=lambda k: size_pressures[k])
        
        base_value_multipliers = {1: 1.0, 2: 1.5, 3: 2.0, 4: 2.5}
        base_value = self.construction_cost_base * base_value_multipliers[most_demanded_size]
        
        new_dwelling = Dwelling(
            dwelling_id=self.next_id,
            size=most_demanded_size,
            base_value=base_value,
            construction_year=self.model.month,
        )
        self.dwellings.append(new_dwelling)
        self.next_id += 1
    
    def handle_inheritance(self, deceased: HouseholdAgent) -> None:
        """Käsittele kuolleen henkilön asunto.
        
        Args:
            deceased: Kuollut agentti
        """
        if deceased.dwelling is None:
            return
        
        dwelling = deceased.dwelling
        
        # Asunto siirtyy myyntiin
        dwelling.owner = None
        dwelling.for_sale = True
        
        # Asunnon arvo siirtyy perinnöksi (hoidetaan HouseholdAgent.die():ssä)
    
    def avg_price_for_size(self, size: int) -> float:
        """v0.7: Palauta keskihinta tietylle asuntokoolle.
        
        Args:
            size: Asunnon koko (1-4)
            
        Returns:
            Keskihinta tai 0 jos ei asuntoja
        """
        size_dwellings = [d for d in self.dwellings if d.size == size]
        if not size_dwellings:
            # Jos ei asuntoja, palauta arvio rakennuskustannuksen perusteella
            base_value_multipliers = {1: 1.0, 2: 1.5, 3: 2.0, 4: 2.5}
            return self.construction_cost_base * base_value_multipliers.get(size, 1.0)
        
        return sum(d.market_value for d in size_dwellings) / len(size_dwellings)
