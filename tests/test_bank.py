from __future__ import annotations

from copy import deepcopy

import pytest

from core.model import EconomyModel


def _base_config() -> dict[str, dict[str, float | int]]:
    return {
        "simulation": {"months": 120},
        "agents": {"households": 1, "firms": 1},
        "households": {
            "initial_cash": 8000.0,
            "propensity_to_consume": 0.2,
            "initial_age_min": 35,
            "initial_age_max": 35,
            "retirement_age": 70,
            "max_age": 120,
            "death_prob_per_year": 0.0,
            "birth_rate_per_year": 0.0,
            "fertile_age_min": 20,
            "fertile_age_max": 45,
            "child_initial_cash": 0.0,
            "cash_floor": 0.0,
            "cash_target": 0.0,
            "debt_service_income_share": 0.25,
            "debt_service_buffer_multiplier": 1.1,
        },
        "firms": {
            "investment_interval_months": 0,
            "investment_loan_amount": 0.0,
            "investment_loan_term": 12,
            "investment_cash_buffer": 0.0,
        },
        "wages": {"initial": 3000.0},
        "taxes": {"income_flat_rate": 0.1, "vat_rate": 0.0},
        "transfers": {"unemployment_benefit": 0.0, "pension": 0.0},
        "banking": {
            "deposit_rate_annual": 0.0,
            "loan_rate_base_annual": 0.02,
            "household_spread": 0.01,
            "firm_spread": 0.015,
            "capital_ratio_min": 0.08,
            "liquidity_buffer_months": 1.0,
            "max_loan_to_income": 6.0,
            "max_debt_service_ratio": 0.45,
            "default_recovery_rate": 0.1,
            "initial_equity": 200000.0,
        },
    }


def _make_model(overrides: dict | None = None) -> EconomyModel:
    cfg = deepcopy(_base_config())
    if overrides:
        for section, data in overrides.items():
            if isinstance(data, dict) and isinstance(cfg.get(section), dict):
                cfg[section].update(data)
            else:
                cfg[section] = data
    return EconomyModel(config=cfg, seed=123)


def test_collect_payments_reduces_balance() -> None:
    model = _make_model()
    bank = model.bank
    borrower = model.households[0]

    assert bank.request_loan(borrower=borrower, amount=10000.0, borrower_type="household", term_months=12)
    loan = bank.loans[-1]
    loan.age_months = 1  # ohitetaan ensimmäinen armahduskuukausi
    starting_balance = loan.balance
    starting_loans = bank.total_loans
    borrower.cash += 5000.0

    bank._collect_payments()

    assert loan.balance < starting_balance
    assert bank.total_loans < starting_loans
    assert bank.last_interest_income > 0
    assert loan.status == "active"


def test_collect_payments_triggers_default_on_shortfall() -> None:
    model = _make_model()
    bank = model.bank
    borrower = model.households[0]

    assert bank.request_loan(borrower=borrower, amount=8000.0, borrower_type="household", term_months=12)
    loan = bank.loans[-1]
    loan.age_months = 1
    borrower.cash = 0.0
    borrower.debt_service_reserve = 0.0
    defaults_before = bank.total_defaulted

    bank._collect_payments()

    assert loan.status == "defaulted"
    assert bank.total_defaulted > defaults_before
    assert bank.loan_metrics.get("nonperforming_balance", 0.0) >= loan.original_balance


def test_money_supply_tracks_loans_without_defaults() -> None:
    overrides = {
        "banking": {
            "deposit_rate_annual": 0.0,
            "loan_rate_base_annual": 0.0,
            "household_spread": 0.0,
            "firm_spread": 0.0,
        }
    }
    model = _make_model(overrides)
    bank = model.bank
    borrower = model.households[0]
    model.firms[0].cash = 100000.0

    assert bank.request_loan(borrower=borrower, amount=6000.0, borrower_type="household", term_months=12)
    gap_before = bank.money_supply - bank.total_loans

    model.run_for_months(12)

    gap_after = bank.money_supply - bank.total_loans
    assert pytest.approx(gap_after, rel=1e-6) == gap_before