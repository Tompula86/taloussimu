from __future__ import annotations

from typing import TYPE_CHECKING

from mesa import Agent

if TYPE_CHECKING:  # pragma: no cover - vain tyyppitarkistukseen
    from core.model import EconomyModel


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
    ):  # type: ignore[no-untyped-def]
        super().__init__(model)
        self.model: EconomyModel = model
        self.age: int = age
        self.employed: bool = age < model.retirement_age
        self.alive: bool = True

        # Tase (v0.2: yksinkertainen versio)
        self.cash: float = initial_cash
        self.real_estate_value: float = 0.0  # Placeholder asunnoille
        self.business_equity: float = 0.0  # Placeholder yrityksille
        self.debt: float = 0.0  # Placeholder veloille

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
        """Kuluta osa käteisestä hyödykemarkkinoilla.

        Palauttaa kulutuksen määrän, jonka yritykset voivat tulouttaa liikevaihdoksi.
        """

        if self.cash <= 0:
            return 0.0

        available_cash = self.available_cash_after_reserve
        if available_cash <= 0:
            return 0.0

        consumption = self.base_propensity_to_consume * available_cash
        self.cash -= consumption
        self.debt_service_reserve = min(self.debt_service_reserve, self.cash)
        return consumption

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
        # v0.3 yksinkertainen arvio: palkkataso työllisillä, muuten työttömyystuki
        if self.employed:
            return self.model.firms[0].wage_level
        return self.model.unemployment_benefit

    @property
    def net_worth(self) -> float:
        """Nettovarallisuus: varat - velat."""
        return self.cash + self.real_estate_value + self.business_equity - self.debt

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
        # Perintö: v0.2 yksinkertainen versio, jaetaan tasan kaikkien elävien kotitalouksien kesken
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
