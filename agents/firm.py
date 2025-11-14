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
    ) -> None:
        super().__init__(model)
        self.wage_level = wage_level
        self.cash: float = 0.0
        self.debt: float = 0.0
        self.capital_stock: float = 0.0
        self.investment_interval_months = max(0, investment_interval_months)
        self.investment_loan_amount = investment_loan_amount
        self.investment_loan_term = max(1, investment_loan_term)
        self.investment_cash_buffer = max(0.0, investment_cash_buffer)
        self.months_since_investment: int = 0

    def pay_wages(self) -> float:
        """Maksetaan palkat yksinkertaiselle osalle kotitalouksista.

        v0.1: jokaiselle kotitaloudelle sama palkka.
        Palauttaa maksettujen palkkojen summan.
        """

        total_wages = 0.0
        for hh in self.model.households:
            # v0.1: kaikki kotitaloudet ovat työllisiä
            hh.receive_income(self.wage_level)
            total_wages += self.wage_level

        shortfall = max(0.0, total_wages - self.cash)
        if shortfall > 0 and hasattr(self.model, "bank"):
            self.model.bank.request_loan(
                borrower=self,
                amount=shortfall,
                borrower_type="firm",
                term_months=12,
                purpose="payroll_bridge",
            )

        self.cash -= total_wages
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
        self._maybe_take_investment_loan()
        self.pay_wages()

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
