from __future__ import annotations

from typing import TYPE_CHECKING, Any

from mesa import Agent

if TYPE_CHECKING:  # pragma: no cover - vain tyyppitarkistukseen
    from core.model import EconomyModel
    from markets.housing import Dwelling
    from agents.firm import FirmAgent


class HouseholdAgent(Agent):
    """Kotitalous v0.2.

    - Elinkaari: ikä, kuolema, perintö
    - Tase: käteinen, reaaliomaisuus (placeholder), yritysomistus (placeholder), velat
    - Päätös: kuluta vs. säästä
    """

    def __init__(
        self,
        model: EconomyModel,
        age: int,
        initial_cash: float = 5000.0,
        propensity: float = 0.8,
        household_size: int = 1,
    ):  # type: ignore[no-untyped-def]
        super().__init__(model)
        self.model: EconomyModel = model
        self.age: int = age
        # v0.7: Työllisyys ja palkka määräytyvät työmarkkinan kautta, eivät iän mukaan
        self.employed: bool = False
        self.alive: bool = True

        # Tase (v0.2: yksinkertainen versio)
        self.cash: float = initial_cash
        self.real_estate_value: float = 0.0  # Placeholder asunnoille
        self.business_equity: float = 0.0  # Placeholder yrityksille
        self.debt: float = 0.0  # Placeholder veloille
        
        # v0.6: Yrittäjyys
        self.owned_firm: FirmAgent | None = None  # Viite FirmAgent:iin (jos omistaa yrityksen)
        self.entrepreneur: bool = False  # Onko yrittäjä

        # v0.5: Kotitalouden koko ja asuminen
        self.household_size: int = household_size  # Montako henkilöä kotitaloudessa
        self.num_children: int = 0  # Lasten määrä
        self.dwelling: Dwelling | None = None  # Viite Dwelling-objektiin (markets.housing) tai None
        self.employer: FirmAgent | None = None  # Viite FirmAgent:iin (työnantaja)
        # v0.7: Henkilökohtainen palkkataso työnantajalta
        self.wage: float = 0.0

        self.base_propensity_to_consume: float = propensity
        self.debt_service_reserve: float = 0.0
        self.debt_service_income_share: float = getattr(
            model,
            "household_debt_service_income_share",
            0.0,
        )
        self.debt_service_buffer_multiplier: float = getattr(
            model,
            "household_debt_service_buffer_multiplier",
            1.0,
        )

    def receive_income(self, gross_wage: float) -> None:
        """Kotitalous saa bruttopalkan yritykseltä.

        Verojen vähennys hoidetaan valtion logiikassa.
        """

        self.cash += gross_wage
        self._allocate_debt_service_share(gross_wage)

    def receive_transfer(self, amount: float) -> None:
        self.cash += amount
        self._allocate_debt_service_share(amount)

    def pay_tax(self, amount: float) -> None:
        self.cash -= amount
        self.debt_service_reserve = min(self.debt_service_reserve, self.cash)

    def consume(self) -> float:
        """v0.4: Kuluta ostamalla hyödykkeitä yrityksiltä dynaamiseen hintaan.

        Palauttaa kulutuksen määrän (netto yritykselle ALV:n jälkeen).
        """

        if self.cash <= 0:
            return 0.0

        available_cash = self.available_cash_after_reserve
        if available_cash <= 0:
            return 0.0

        consumption_budget = self.base_propensity_to_consume * available_cash
        if consumption_budget <= 0:
            return 0.0

        # v0.4: Osta satunnaiselta yritykseltä
        # v0.6: Vain elossa olevat yritykset
        # Myöhemmin: Osta halvimmalla hinnalla
        alive_firms = [f for f in self.model.firms if f.alive]
        if not alive_firms:
            return 0.0

        target_firm = self.random.choice(alive_firms)

        if target_firm.price <= 0:
            return 0.0

        units_to_buy = consumption_budget / target_firm.price

        # Suorita osto
        actual_spent = target_firm.sell_goods(units_to_buy)
        self.cash -= actual_spent
        self.debt_service_reserve = min(self.debt_service_reserve, self.cash)

        # ALV maksetaan heti tässä (v0.8: käytetään state.collect_vat)
        vat_amount = actual_spent * self.model.vat_rate
        self.model.state.collect_vat(vat_amount)

        # Palauta kulutettu summa (nettona yritykselle)
        return actual_spent - vat_amount

    def receive_loan(self, amount: float) -> None:
        self.cash += amount

    def increase_debt(self, amount: float) -> None:
        self.debt += amount

    def decrease_debt(self, amount: float) -> None:
        self.debt = max(0.0, self.debt - amount)

    def pay_debt(self, amount: float) -> float:
        payment = min(self.cash, amount)
        self.cash -= payment
        self.debt_service_reserve = max(0.0, self.debt_service_reserve - payment)
        return payment

    def expected_monthly_income(self) -> float:
        """v0.7: Odotettu kuukausitulo perustuu omaan palkkaan tai työttömyystukeen."""
        if self.employed:
            return self.wage
        return self.model.unemployment_benefit

    @property
    def net_worth(self) -> float:
        """Nettovarallisuus: varat - velat."""
        # v0.5: Asunnon arvo lasketaan dwelling-objektista
        dwelling_value = self.dwelling.market_value if self.dwelling else 0.0
        return self.cash + dwelling_value + self.business_equity - self.debt
    
    def needs_housing(self) -> bool:
        """v0.5: Tarvitseeko kotitalous asunnon?
        
        Returns:
            True jos:
            1. Ei omista asuntoa + on työssä + on aikuinen, TAI
            2. Omistaa asunnon, mutta perhe kasvanut liian isoksi
        """
        # Ei omista + työssä + aikuinen
        if self.dwelling is None and self.employed and self.age >= 20:
            return True
        
        # Omistaa, mutta perhe kasvanut liian isoksi (> 1.5x asunnon koko)
        if self.dwelling is not None:
            if self.household_size > self.dwelling.size * 1.5:
                return True  # Päivitystarve
        
        return False
    
    def required_dwelling_size(self) -> int:
        """v0.5: Tarvittava asunnon koko kotitalouden koon mukaan.
        
        Returns:
            1=yksiö, 2=kaksio, 3=kolmio, 4=neliö+
        """
        if self.household_size == 1:
            return 1  # Yksiö
        elif self.household_size == 2:
            return 2  # Kaksio
        elif self.household_size <= 4:
            return 3  # Kolmio
        else:
            return 4  # Neliö+

    def age_one_month(self) -> None:
        """Ikäänny yksi kuukausi ja tarkista kuolema."""
        # Ikääntäminen kuukausittain (12 kk = 1 vuosi)
        if self.model.month % 12 == 0:
            self.age += 1

        # Kuolemanriski (yksinkertaistettu)
        import random
        if self.age >= self.model.max_age or random.random() < self.model.death_prob_per_year / 12:
            self.die()

    def die(self) -> None:
        """Agentti kuolee ja perintö siirtyy."""
        self.alive = False
        
        # v0.5: Asunto siirtyy myyntiin
        if self.dwelling is not None:
            housing_market = getattr(self.model, 'housing_market', None)
            if housing_market:
                housing_market.handle_inheritance(self)
        
        # Perintö: v0.5 parannettu versio (sisältää asunnon arvon)
        if self.net_worth > 0:
            living_households = [h for h in self.model.households if h.alive and h != self]
            if living_households:
                inheritance_per_hh = self.net_worth / len(living_households)
                for hh in living_households:
                    hh.cash += inheritance_per_hh
        
        # Nollataan oma varallisuus
        self.cash = 0.0
        self.real_estate_value = 0.0
        self.business_equity = 0.0
        self.debt = 0.0
        self.dwelling = None

    def lose_job(self) -> None:
        """v0.7: Menetä työpaikka ja nollaa palkka."""
        self.employed = False
        self.employer = None
        self.wage = 0.0

    def check_leaving_home(self) -> None:
        """v0.5: Tarkista, muuttaako joku lapsista pois kotoa.
        
        Nuoret muuttavat pois 18-25v välillä, luoden uuden kotitalouden
        ja asunnon tarpeen ("pesästä lentäminen").
        """
        if self.num_children == 0:
            return
        
        # Kuukausittainen todennäköisyys, että joku lapsista muuttaa pois
        leaving_home_rate = getattr(self.model, 'leaving_home_rate_per_month', 0.01)
        
        if self.random.random() < leaving_home_rate:
            # Lapsi muuttaa pois
            self.household_size -= 1
            self.num_children -= 1
            
            # Luodaan uusi "pesästä lentäjä" -agentti
            young_adult = HouseholdAgent(
                model=self.model,
                age=self.random.randint(18, 25),
                initial_cash=self.model.child_initial_cash,
                propensity=self.base_propensity_to_consume,
                household_size=1,
            )
            self.model.households.append(young_adult)

    def step(self) -> None:
        if not self.alive:
            return

        # Ikääntyminen ja kuolema
        self.age_one_month()

        if not self.alive:
            return

        # Eläkkeelle jääminen
        if self.age >= self.model.retirement_age:
            self.employed = False
        
        # v0.5: Tarkista pesästä lentäminen
        self.check_leaving_home()
        
        # v0.6: Yrittäjyys
        if not self.entrepreneur:
            self.try_start_business()

        # Pyydä kulutusluottoa, jos kassa on alle puskurin
        self.rebalance_debt_service_reserve()
        self.maybe_request_loan()

        # Kulutus
        consumption = self.consume()
        self.model.total_consumption += consumption

    def maybe_request_loan(self) -> None:
        bank = getattr(self.model, "bank", None)
        if bank is None:
            return
        if self.available_cash_after_reserve >= self.model.household_cash_floor:
            return

        needed = max(0.0, self.model.household_cash_target - self.available_cash_after_reserve)
        if needed <= 0:
            return

        bank.request_loan(
            borrower=self,
            amount=needed,
            borrower_type="household",
            term_months=24,
            purpose="buffer_top_up",
        )

    @property
    def available_cash_after_reserve(self) -> float:
        return max(0.0, self.cash - self.debt_service_reserve)

    def _allocate_debt_service_share(self, inflow: float) -> None:
        if inflow <= 0 or self.debt_service_income_share <= 0:
            return
        allocation = inflow * self.debt_service_income_share
        self.debt_service_reserve = min(self.cash, self.debt_service_reserve + allocation)

    def rebalance_debt_service_reserve(self) -> None:
        bank = getattr(self.model, "bank", None)
        if bank is None:
            self.debt_service_reserve = 0.0
            return
        expected_payment = bank.expected_payment_for(self)
        if expected_payment <= 0:
            self.debt_service_reserve = 0.0
            return
        target = expected_payment * self.debt_service_buffer_multiplier
        self.debt_service_reserve = min(self.cash, target)
    
    def try_start_business(self) -> None:
        """v0.6: Yritä perustaa yritys.
        
        Edellytykset:
        - Ikä 25-55 vuotta
        - Ei ole vielä yrittäjä
        - Tarpeeksi alkupääomaa (siemenpääoma + puskuri)
        - Kuukausittainen pieni todennäköisyys
        """
        # Tarkista edellytykset
        if self.entrepreneur or self.owned_firm is not None:
            return
        
        if not (25 <= self.age <= 55):
            return
        
        entrepreneurship_rate = getattr(self.model, 'entrepreneurship_rate_per_month', 0.001)
        if self.random.random() > entrepreneurship_rate:
            return
        
        # Siemenpääoma + puskuri
        seed_capital = getattr(self.model, 'firm_seed_capital', 10000.0)
        cash_buffer = getattr(self.model, 'entrepreneur_cash_buffer', 5000.0)
        
        if self.cash < seed_capital + cash_buffer:
            return
        
        # Perusta yritys!
        from agents.firm import FirmAgent
        
        # v0.6: Käytä elossa olevien yritysten palkkatason keskiarvoa
        alive_firms = [f for f in self.model.firms if f.alive]
        avg_wage = sum(f.wage_level for f in alive_firms) / len(alive_firms) if alive_firms else 2500.0
        
        new_firm = FirmAgent(
            model=self.model,
            wage_level=avg_wage,
            investment_interval_months=24,
            investment_loan_amount=50000.0,
            investment_loan_term=60,
            investment_cash_buffer=10000.0,
            owner=self,
            initial_equity=seed_capital,
        )
        
        # Siirrä siemenpääoma
        self.cash -= seed_capital
        new_firm.cash = seed_capital
        new_firm.equity = seed_capital
        
        # Rekisteröi yritys
        self.model.firms.append(new_firm)
        self.owned_firm = new_firm
        self.entrepreneur = True
        self.business_equity = seed_capital
        
        # Yritys tarvitsee lainaa toimintaansa käynnistämiseen
        bank = getattr(self.model, 'bank', None)
        if bank is not None:
            business_loan = getattr(self.model, 'startup_business_loan', 30000.0)
            bank.request_loan(
                borrower=new_firm,
                amount=business_loan,
                borrower_type="firm",
                term_months=60,
                purpose="startup",
            )
    
    def handle_business_bankruptcy(self, firm) -> None:
        """v0.6: Käsittele oman yrityksen konkurssi.
        
        Omistaja menettää sijoittamansa pääoman.
        """
        if self.owned_firm == firm:
            self.business_equity = 0.0
            self.owned_firm = None
            self.entrepreneur = False
