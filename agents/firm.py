from __future__ import annotations

from mesa import Agent


class FirmAgent(Agent):
    """Yritys v0.1.

    - Maksaa palkkaa kotitalouksille (yksinkertaistettuna sama palkka kaikille työllisille)
    - Saa tuloja kotitalouksien kulutuksesta
    - Ei vielä dynaamista työllistämis-/hinnoittelupäätöstä
    """

    def __init__(
        self,
        model,
        wage_level: float,
        investment_interval_months: int,
        investment_loan_amount: float,
        investment_loan_term: int,
        investment_cash_buffer: float,
        owner=None,
        initial_equity: float = 0.0,
    ) -> None:
        super().__init__(model)
        # v0.7: Yrityksen tarjoama palkkataso työpaikoille
        self.wage_level = wage_level
        self.cash: float = 0.0
        self.debt: float = 0.0
        self.capital_stock: float = 0.0
        self.investment_interval_months = max(0, investment_interval_months)
        self.investment_loan_amount = investment_loan_amount
        self.investment_loan_term = max(1, investment_loan_term)
        self.investment_cash_buffer = max(0.0, investment_cash_buffer)
        self.months_since_investment: int = 0
        
        # v0.4: Dynaaminen hinnoittelu ja varasto
        self.price: float = 1.0  # Aloitushinta yhdelle tuotteelle
        self.inventory: float = 100.0  # Aloitusvarasto
        self.production_per_month: float = 20.0  # Paljonko tuotetaan kuussa
        self.target_inventory: float = 100.0  # Tavoitevarasto
        
        # v0.6: Yrittäjyys ja konkurssit
        self.owner = owner  # Viite HouseholdAgent:iin (jos yrittäjäyritys)
        self.equity: float = initial_equity  # Oma pääoma
        self.alive: bool = True  # Onko yritys toiminnassa
        self.founded_month: int = model.month  # Milloin perustettu
        self.is_startup: bool = owner is not None  # Onko uusi yrittäjäyritys
        # v0.7: Työvoima
        self.employees: list["HouseholdAgent"] = []
        self.target_employees: int = 0

    def pay_wages(self) -> float:
        """v0.7: Maksa palkat vain omille työntekijöille."""

        total_wages = 0.0
        for employee in list(self.employees):
            wage = getattr(employee, "wage", self.wage_level)
            if self.cash >= wage:
                self.cash -= wage
                employee.receive_income(wage)
                total_wages += wage
            else:
                # Maksukyvyttömyys palkoista → konkurssi
                self._go_bankrupt()
                break
        return total_wages

    def receive_revenue(self, amount: float) -> None:
        self.cash += amount

    def receive_loan(self, amount: float) -> None:
        self.cash += amount

    def increase_debt(self, amount: float) -> None:
        self.debt += amount

    def decrease_debt(self, amount: float) -> None:
        self.debt = max(0.0, self.debt - amount)

    def pay_debt(self, amount: float) -> float:
        payment = min(self.cash, amount)
        self.cash -= payment
        return payment

    def receive_deposit_interest(self, amount: float) -> None:
        self.cash += amount

    def step(self) -> None:
        if not self.alive:
            return
        
        # v0.7: Päivitä työvoimakysyntä ja palkkataso ennen tuotantoa
        self._update_labor_demand()
        self._update_wage_level()
        
        self._produce()
        self._update_price()
        self._maybe_take_investment_loan()
        self.pay_wages()
        self.check_bankruptcy()

    def _update_labor_demand(self) -> None:
        """v0.7: Päivitä tavoitetyöntekijämäärä varastotilanteen mukaan."""
        if self.inventory < self.target_inventory * 0.8:
            self.target_employees += 1
        elif self.inventory > self.target_inventory * 1.2:
            self.target_employees = max(0, self.target_employees - 1)

    def _update_wage_level(self) -> None:
        """v0.7: Säädä tarjottavaa palkkatasoa työttömyysasteen mukaan."""
        unemployment = getattr(self.model, "unemployment_rate", 0.0)
        if unemployment < 0.05:
            self.wage_level *= 1.01
        elif unemployment > 0.10:
            self.wage_level *= 0.99

    def _produce(self) -> None:
        """v0.4: Tuotanto lisää varastoa kuukausittain."""
        self.inventory += self.production_per_month

    def _update_price(self) -> None:
        """v0.4: Yksinkertainen inventory targeting -hinnoittelusääntö.
        
        Jos varasto on alle 80% tavoitteesta → nosta hintaa (inflaatio)
        Jos varasto on yli 120% tavoitteesta → laske hintaa (deflaatio)
        """
        if self.inventory < self.target_inventory * 0.8:
            self.price *= 1.02  # Nosta hintaa 2%
        elif self.inventory > self.target_inventory * 1.2:
            self.price *= 0.98  # Laske hintaa 2%

    def sell_goods(self, units: float) -> float:
        """v0.4: Myy tuotteita ja palauttaa myynnin arvon.
        
        Args:
            units: Haluttu ostosmäärä
            
        Returns:
            Myydyn tavaran arvo (hinta × tosiasiallinen määrä)
        """
        units_to_sell = min(self.inventory, units)
        revenue = units_to_sell * self.price
        self.inventory -= units_to_sell
        self.receive_revenue(revenue)
        return revenue

    def _maybe_take_investment_loan(self) -> None:
        if self.investment_interval_months <= 0:
            return

        self.months_since_investment += 1
        if self.months_since_investment < self.investment_interval_months:
            return

        bank = getattr(self.model, "bank", None)
        if bank is None or bank.stop_lending:
            return

        if self.cash < self.investment_cash_buffer:
            return

        granted = bank.request_loan(
            borrower=self,
            amount=self.investment_loan_amount,
            borrower_type="firm",
            term_months=self.investment_loan_term,
            purpose="investment",
        )
        if granted:
            # Pidetään kirjaa pääomakannasta ja kirjataan investointi heti kassasta ulos
            self.capital_stock += self.investment_loan_amount
            self.cash -= self.investment_loan_amount
            self.months_since_investment = 0

    def check_bankruptcy(self) -> None:
        """v0.6: Tarkista onko yritys maksukyvytön.
        
        Konkurssikriteeri: Velka > Varat JA negatiivinen kassa
        Eli ei pysty maksamaan juoksevia kuluja eikä ole omaisuutta myytäväksi.
        """
        if not self.alive:
            return
            
        total_assets = self.cash + self.capital_stock + self.inventory * self.price
        
        # Konkurssi jos velka ylittää varat JA kassa on negatiivinen
        if self.debt > total_assets and self.cash < 0:
            self._go_bankrupt()
    
    def _go_bankrupt(self) -> None:
        """Suorita konkurssi."""
        self.alive = False
        
        # Ilmoita omistajalle (jos yrittäjäyritys)
        if self.owner is not None:
            self.owner.handle_business_bankruptcy(self)
        
        # v0.7: Vapauta omat työntekijät tehokkaasti
        for employee in list(self.employees):
            employee.lose_job()
        self.employees.clear()
        
        # Pankki kirjaa tappion (yrityksen varat ei riitä velkaan)
        if hasattr(self.model, "bank"):
            # Varat menevät konkurssipesään, pankki saa osan
            recovery_value = max(0.0, self.cash + self.capital_stock + self.inventory * self.price)
            self.model.bank.handle_firm_bankruptcy(self, recovery_value)
