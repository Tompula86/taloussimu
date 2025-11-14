from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from typing import Any

from mesa import Agent


@dataclass
class LoanRecord:
    borrower: Any
    borrower_type: str
    balance: float
    annual_rate: float
    term_months: int
    remaining_term: int
    status: str = "active"
    age_months: int = 0
    purpose: str = "general"
    original_balance: float = 0.0

    @property
    def monthly_rate(self) -> float:
        return self.annual_rate / 12.0


class BankAgent(Agent):
    """Yksinkertainen pankki v0.3.

    - Myöntää lainoja kotitalouksille ja yrityksille
    - Maksaa talletuskorkoa ja kerää lainojen lyhennyksiä
    - Seuraa perusmittareita (rahakanta, pääomasuhde, defaultit)
    """

    def __init__(self, model, config: dict[str, Any] | None = None):  # type: ignore[no-untyped-def]
        super().__init__(model)
        config = config or {}

        self.deposit_rate_annual: float = float(config.get("deposit_rate_annual", 0.0))
        self.loan_rate_base_annual: float = float(config.get("loan_rate_base_annual", 0.02))
        self.household_spread: float = float(config.get("household_spread", 0.02))
        self.firm_spread: float = float(config.get("firm_spread", 0.025))
        self.capital_ratio_min: float = float(config.get("capital_ratio_min", 0.08))
        self.liquidity_buffer_months: float = float(config.get("liquidity_buffer_months", 3.0))
        self.max_loan_to_income: float = float(config.get("max_loan_to_income", 4.0))
        self.max_debt_service_ratio: float = float(config.get("max_debt_service_ratio", 0.35))
        self.default_recovery_rate: float = float(config.get("default_recovery_rate", 0.2))
        self.initial_equity: float = float(config.get("initial_equity", 100000.0))

        self.deposit_rate_monthly: float = self.deposit_rate_annual / 12.0
        self.loans: list[LoanRecord] = []
        self.total_loans: float = 0.0
        self.total_deposits: float = 0.0
        self.total_defaulted: float = 0.0
        self.equity: float = self.initial_equity
        self.cash_reserves: float = self.initial_equity
        self.stop_lending: bool = False
        self.loan_metrics: dict[str, float] = {}
        self.loan_metrics_history: list[dict[str, float]] = []
        self._loan_age_buckets: tuple[tuple[str, int, float], ...] = (
            ("0_6", 0, 6),
            ("6_12", 6, 12),
            ("12_24", 12, 24),
            ("24_plus", 24, float("inf")),
        )

        # Mittarit viimeiseltä stepiltä (debug)
        self.last_interest_income: float = 0.0
        self.last_defaults: float = 0.0
        self.last_deposit_interest_paid: float = 0.0

        # Oleta, että olemassa olevat kotitalous- ja yritystalletukset ovat pankin vastuuta
        initial_deposits = self._estimate_initial_deposits()
        if initial_deposits > 0:
            self.total_deposits += initial_deposits
            self.cash_reserves += initial_deposits
        self._update_loan_metrics()

    # --- Julkinen API ---
    def request_loan(
        self,
        borrower: Any,
        amount: float,
        borrower_type: str = "household",
        term_months: int = 24,
        purpose: str = "general",
    ) -> bool:
        amount = float(amount)
        if amount <= 0:
            return False

        if term_months <= 0:
            term_months = 12

        if not self._can_lend(amount, borrower, borrower_type, term_months):
            return False

        rate = self._loan_rate_for(borrower_type)
        record = LoanRecord(
            borrower=borrower,
            borrower_type=borrower_type,
            balance=amount,
            annual_rate=rate,
            term_months=term_months,
            remaining_term=term_months,
            purpose=purpose,
            original_balance=amount,
        )
        self.loans.append(record)

        self.total_loans += amount
        self.total_deposits += amount
        borrower.receive_loan(amount)
        borrower.increase_debt(amount)
        self._update_loan_metrics()
        return True

    def record_new_deposit(self, amount: float) -> None:
        if amount <= 0:
            return
        self.total_deposits += amount
        self.cash_reserves += amount

    def step(self) -> None:
        self.last_interest_income = 0.0
        self.last_defaults = 0.0
        self.last_deposit_interest_paid = 0.0

        self._collect_payments()
        self._pay_deposit_interest()
        self._update_stop_lending_flag()
        self._update_loan_metrics(log_snapshot=True)

    # --- Sisäiset apurit ---
    def _collect_payments(self) -> None:
        for loan in list(self.loans):
            if loan.status != "active":
                continue
            if loan.balance <= 1e-6:
                loan.status = "repaid"
                continue

            if loan.age_months == 0:
                loan.age_months += 1
                continue

            payment_target = self._annuity_payment(loan.balance, loan.monthly_rate, loan.remaining_term)
            interest_due = loan.balance * loan.monthly_rate
            principal_due = max(payment_target - interest_due, 0.0)
            total_due = interest_due + principal_due

            paid = loan.borrower.pay_debt(total_due)
            if paid + 1e-9 < interest_due:
                self._apply_default(loan)
                continue

            interest_paid = min(interest_due, paid)
            principal_paid = max(0.0, paid - interest_paid)

            loan.balance -= principal_paid
            loan.remaining_term = max(loan.remaining_term - 1, 0)
            loan.age_months += 1
            loan.borrower.decrease_debt(principal_paid)

            self.total_loans = max(0.0, self.total_loans - principal_paid)
            self.total_deposits = max(0.0, self.total_deposits - paid)
            self.cash_reserves += paid
            self.equity += interest_paid
            self.last_interest_income += interest_paid

            if loan.balance <= 1e-6 or loan.remaining_term <= 0:
                loan.status = "repaid"
        self._update_loan_metrics()

    def _apply_default(self, loan: LoanRecord) -> None:
        balance = loan.balance
        loss = balance * (1.0 - self.default_recovery_rate)
        recovery = balance * self.default_recovery_rate

        self.total_loans = max(0.0, self.total_loans - balance)
        self.cash_reserves += recovery
        self.equity -= loss
        self.total_defaulted += loss
        self.last_defaults += loss

        loan.borrower.decrease_debt(balance)
        loan.balance = 0.0
        loan.remaining_term = 0
        loan.status = "defaulted"
        self._update_loan_metrics()

    def _pay_deposit_interest(self) -> None:
        if self.deposit_rate_monthly <= 0 or self.total_deposits <= 0:
            return

        total_interest = 0.0
        for hh in getattr(self.model, "households", []):
            if not getattr(hh, "alive", True):
                continue
            if hh.cash <= 0:
                continue
            interest = hh.cash * self.deposit_rate_monthly
            hh.receive_income(interest)
            total_interest += interest

        for firm in getattr(self.model, "firms", []):
            if firm.cash <= 0:
                continue
            interest = firm.cash * self.deposit_rate_monthly
            firm.receive_deposit_interest(interest)
            total_interest += interest

        if total_interest == 0.0:
            return

        self.total_deposits += total_interest
        self.cash_reserves -= total_interest
        self.equity -= total_interest
        self.last_deposit_interest_paid = total_interest

    def _update_stop_lending_flag(self) -> None:
        self.stop_lending = self.capital_ratio < self.capital_ratio_min or self._liquidity_stressed()

    def _can_lend(
        self,
        amount: float,
        borrower: Any,
        borrower_type: str,
        term_months: int,
    ) -> bool:
        if self.stop_lending:
            return False

        projected_loans = self.total_loans + amount
        if projected_loans <= 0:
            return True

        projected_ratio = self.equity / projected_loans
        if projected_ratio < self.capital_ratio_min:
            return False

        if borrower_type == "household":
            income = getattr(borrower, "expected_monthly_income", lambda: 0.0)()
            if income <= 0:
                return False
            max_by_income = self.max_loan_to_income * income * 12.0
            if borrower.debt + amount > max_by_income:
                return False

            monthly_rate = self._loan_rate_for(borrower_type) / 12.0
            payment = self._annuity_payment(amount, monthly_rate, term_months)
            if payment > self.max_debt_service_ratio * income:
                return False

        return not self._liquidity_stressed()

    def _liquidity_stressed(self) -> bool:
        if self.deposit_rate_monthly <= 0:
            return False
        projected_interest_outflow = self.total_deposits * self.deposit_rate_monthly
        required_buffer = projected_interest_outflow * self.liquidity_buffer_months
        return self.cash_reserves < required_buffer

    def _loan_rate_for(self, borrower_type: str) -> float:
        if borrower_type == "firm":
            return self.loan_rate_base_annual + self.firm_spread
        return self.loan_rate_base_annual + self.household_spread

    def expected_payment_for(self, borrower: Any) -> float:
        total = 0.0
        for loan in self.loans:
            if loan.borrower is not borrower or loan.status != "active":
                continue
            total += self._annuity_payment(loan.balance, loan.monthly_rate, max(loan.remaining_term, 1))
        return total

    @staticmethod
    def _annuity_payment(balance: float, monthly_rate: float, term_months: int) -> float:
        term_months = max(term_months, 1)
        if monthly_rate <= 0:
            return balance / term_months

        factor = (monthly_rate * (1 + monthly_rate) ** term_months) / ((1 + monthly_rate) ** term_months - 1)
        return balance * factor

    def _estimate_initial_deposits(self) -> float:
        households = getattr(self.model, "households", [])
        firms = getattr(self.model, "firms", [])
        total = 0.0
        total += sum(getattr(h, "cash", 0.0) for h in households)
        total += sum(getattr(f, "cash", 0.0) for f in firms)
        return total

    # --- Johdetut suureet ---
    @property
    def capital_ratio(self) -> float:
        if self.total_loans <= 0:
            return 1.0
        return max(0.0, self.equity / self.total_loans)

    @property
    def money_supply(self) -> float:
        return max(0.0, self.total_deposits)

    @property
    def active_loans(self) -> list[LoanRecord]:
        return [loan for loan in self.loans if loan.status == "active"]

    def _update_loan_metrics(self, log_snapshot: bool = False) -> None:
        active_loans = [loan for loan in self.loans if loan.status == "active" and loan.balance > 0]
        outstanding_balance = sum(loan.balance for loan in active_loans)
        defaulted_balance = sum(loan.original_balance for loan in self.loans if loan.status == "defaulted")
        denominator = outstanding_balance + defaulted_balance
        performing_share = outstanding_balance / denominator if denominator > 0 else 1.0
        avg_age = sum(loan.age_months for loan in active_loans) / len(active_loans) if active_loans else 0.0

        bucket_totals: dict[str, float] = {f"age_bucket_{label}_share": 0.0 for label, _, _ in self._loan_age_buckets}
        purpose_totals: dict[str, float] = defaultdict(float)
        for loan in active_loans:
            label = self._loan_age_bucket_label(loan.age_months)
            bucket_key = f"age_bucket_{label}_share"
            bucket_totals[bucket_key] += loan.balance
            purpose_totals[f"purpose_{loan.purpose}_share"] += loan.balance

        if outstanding_balance > 0:
            for key in bucket_totals:
                bucket_totals[key] /= outstanding_balance
            for key in list(purpose_totals.keys()):
                purpose_totals[key] /= outstanding_balance

        metrics: dict[str, float] = {
            "active_balance": outstanding_balance,
            "performing_share": performing_share,
            "nonperforming_balance": defaulted_balance,
            "avg_active_age": avg_age,
        }
        metrics.update(bucket_totals)
        metrics.update(purpose_totals)
        self.loan_metrics = metrics

        if log_snapshot:
            month = getattr(self.model, "month", len(self.loan_metrics_history))
            self.loan_metrics_history.append({"month": month, **metrics})

    def _loan_age_bucket_label(self, age_months: int) -> str:
        for label, start, end in self._loan_age_buckets:
            if start <= age_months < end:
                return label
        return self._loan_age_buckets[-1][0]