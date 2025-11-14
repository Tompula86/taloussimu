from __future__ import annotations

from mesa import Agent


class StateAgent(Agent):
    """Valtio v0.1.

    - Perii tasaveron palkkatuloista
    - Maksaa työttömyyskorvausta ja eläkettä (v0.1 vain yksinkertainen tuki kaikille)
    """

    def __init__(self, model):  # type: ignore[no-untyped-def]
        super().__init__(model)
        self.cash_balance: float = 0.0

    def collect_income_tax(self) -> None:
        tax_rate = self.model.tax_rate
        for hh in self.model.households:
            # v0.1: oletetaan, että viime kuun palkka oli model.firms[0].wage_level
            # ja että kaikki tulot ovat verotettavaa palkkaa
            # (yksinkertainen esiversio)
            taxable = self.model.firms[0].wage_level if hh.employed else 0.0
            tax = tax_rate * taxable
            if tax > 0:
                hh.pay_tax(tax)
                self.cash_balance += tax

    def pay_transfers(self) -> None:
        """Maksa yksinkertaiset tulonsiirrot.

        v0.1: sama peruskorvaus kaikille kotitalouksille.
        """

        benefit = self.model.unemployment_benefit
        for hh in self.model.households:
            hh.receive_transfer(benefit)
            self.cash_balance -= benefit

    def step(self) -> None:
        # v0.1: ensin verot, sitten tulonsiirrot
        self.collect_income_tax()
        self.pay_transfers()
