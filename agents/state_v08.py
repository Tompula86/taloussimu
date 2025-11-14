"""Valtion agentti v0.8.

Toteuttaa realistisen valtion toiminnan:
- Progressiivinen tulovero
- Yritysvero
- Arvonlisävero (VAT)
- Pääomatulovero
- Kohdennetut tulonsiirrot (työttömyys, eläke)
- Budjettiseuranta ja velkamekanismi
- Julkiset hankinnat
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from mesa import Agent

if TYPE_CHECKING:  # pragma: no cover
    from core.model import EconomyModel
    from agents.household import HouseholdAgent
    from agents.firm import FirmAgent


class StateAgent(Agent):
    """Valtio v0.8.
    
    Kerää progressiivisia veroja ja maksaa kohdennettuja tulonsiirtoja.
    Seuraa budjettia ja velkaa. Tekee julkisia hankintoja.
    """
    
    def __init__(self, model: EconomyModel):
        super().__init__(model)
        self.model: EconomyModel = model
        
        # Tase ja budjetti
        self.cash_balance: float = 0.0
        self.total_debt: float = 0.0
        
        # Kuukausittaiset seurattavat (nollataan joka kuukausi)
        self.monthly_revenue: float = 0.0
        self.monthly_expenses: float = 0.0
        
        # Tulojen erittely
        self.income_tax_revenue: float = 0.0
        self.corporate_tax_revenue: float = 0.0
        self.vat_revenue: float = 0.0
        self.capital_gains_revenue: float = 0.0
        
        # Menojen erittely
        self.transfer_expenses: float = 0.0
        self.debt_service_expenses: float = 0.0
        self.public_procurement_expenses: float = 0.0
        
        # Parametrit (ladataan konfiguraatiosta)
        self._load_config()
    
    def _load_config(self) -> None:
        """Lataa veroparametrit konfiguraatiosta tai käytä oletuksia."""
        # Progressiivinen tuloveroasteikko
        taxes_cfg = getattr(self.model, '_config', {}).get('taxes', {})
        
        # Oletusasteikko jos ei konfiguroitu
        default_brackets = [
            (0.0, 15000.0, 0.05),
            (15000.0, 30000.0, 0.15),
            (30000.0, 50000.0, 0.25),
            (50000.0, float('inf'), 0.35),
        ]
        
        brackets_config = taxes_cfg.get('income_brackets', default_brackets)
        self.income_tax_brackets = []
        for bracket in brackets_config:
            if len(bracket) == 3:
                lower, upper, rate = bracket
                # Muunna 'inf' stringistä floatiksi jos tarvii
                if isinstance(upper, str) and upper == '.inf':
                    upper = float('inf')
                self.income_tax_brackets.append((float(lower), float(upper), float(rate)))
        
        # Muut veroparametrit
        self.corporate_tax_rate: float = float(taxes_cfg.get('corporate_rate', 0.20))
        self.vat_rate: float = float(taxes_cfg.get('vat_rate', self.model.vat_rate))
        self.capital_gains_rate: float = float(taxes_cfg.get('capital_gains_rate', 0.30))
        
        # Valtion parametrit
        state_cfg = getattr(self.model, '_config', {}).get('state', {})
        self.debt_interest_rate_annual: float = float(state_cfg.get('debt_interest_rate', 0.03))
        self.public_spending_share: float = float(state_cfg.get('public_spending_share', 0.15))
        
        # Tulonsiirrot
        self.unemployment_benefit: float = self.model.unemployment_benefit
        self.pension: float = self.model.pension
    
    def reset_monthly_counters(self) -> None:
        """Nollaa kuukausittaiset laskurit."""
        self.monthly_revenue = 0.0
        self.monthly_expenses = 0.0
        self.income_tax_revenue = 0.0
        self.corporate_tax_revenue = 0.0
        self.vat_revenue = 0.0
        self.capital_gains_revenue = 0.0
        self.transfer_expenses = 0.0
        self.debt_service_expenses = 0.0
        self.public_procurement_expenses = 0.0
    
    # ==================== TULOT (REVENUE) ====================
    
    def collect_income_tax(self) -> None:
        """Kerää progressiivinen tulovero kotitalouksien palkkatuloista."""
        total_tax = 0.0
        
        for hh in self.model.households:
            if not hh.alive or not hh.employed:
                continue
            
            # Perustuu henkilökohtaiseen palkkaan (v0.7)
            monthly_income = hh.wage
            
            if monthly_income <= 0:
                continue
            
            # Lasketaan vuosittainen vero progressiivisen asteikon mukaan
            annual_income = monthly_income * 12
            annual_tax = self._calculate_progressive_tax(annual_income)
            monthly_tax = annual_tax / 12.0
            
            # Varmistetaan ettei vero ylitä tuloa
            tax_to_pay = min(monthly_tax, monthly_income)
            
            if tax_to_pay > 0:
                hh.pay_tax(tax_to_pay)
                total_tax += tax_to_pay
        
        self.income_tax_revenue = total_tax
        self.monthly_revenue += total_tax
        self.cash_balance += total_tax
    
    def _calculate_progressive_tax(self, annual_income: float) -> float:
        """Laskee veron määrän progressiivisen asteikon mukaan."""
        total_tax = 0.0
        
        for lower, upper, rate in self.income_tax_brackets:
            if annual_income > lower:
                taxable_in_bracket = min(annual_income, upper) - lower
                total_tax += taxable_in_bracket * rate
            else:
                break
        
        return total_tax
    
    def collect_corporate_tax(self) -> None:
        """Kerää yritysveron yritysten voitoista."""
        total_tax = 0.0
        
        for firm in self.model.firms:
            if not firm.alive:
                continue
            
            # Laske kuukauden voitto (Tulot - Menot)
            profit = firm.revenue_this_month - firm.expenses_this_month
            
            if profit > 0:
                tax_to_pay = profit * self.corporate_tax_rate
                
                # Varmistetaan että yrityksellä on varaa maksaa
                if firm.cash >= tax_to_pay:
                    firm.cash -= tax_to_pay
                    total_tax += tax_to_pay
        
        self.corporate_tax_revenue = total_tax
        self.monthly_revenue += total_tax
        self.cash_balance += total_tax
    
    def collect_vat(self, amount: float) -> None:
        """Passiivinen metodi ALV:n keräämiseen.
        
        Kutsutaan HouseholdAgent.consume():ssa ostohetkellä.
        """
        self.vat_revenue += amount
        self.monthly_revenue += amount
        self.cash_balance += amount
    
    def collect_capital_gains_tax(self, household: HouseholdAgent, capital_gain: float) -> None:
        """Kerää pääomatuloveron asunnon myyntivoitosta.
        
        Args:
            household: Myyjä
            capital_gain: Myyntivoitto (sale_price - purchase_price)
        """
        if capital_gain <= 0:
            return
        
        tax = capital_gain * self.capital_gains_rate
        
        # Varmistetaan että kotitaloudella on varaa maksaa
        if household.cash >= tax:
            household.cash -= tax
            self.capital_gains_revenue += tax
            self.monthly_revenue += tax
            self.cash_balance += tax
    
    # ==================== MENOT (EXPENSES) ====================
    
    def pay_transfers(self) -> None:
        """Maksa kohdennetut tulonsiirrot."""
        total_paid = 0.0
        retirement_age = self.model.retirement_age
        
        for hh in self.model.households:
            if not hh.alive:
                continue
            
            # Eläkkeet (vain eläkeläisille)
            if hh.age >= retirement_age:
                hh.receive_transfer(self.pension)
                total_paid += self.pension
            
            # Työttömyystuki (vain työttömille työikäisille)
            elif not hh.employed:
                hh.receive_transfer(self.unemployment_benefit)
                total_paid += self.unemployment_benefit
        
        self.transfer_expenses = total_paid
        self.monthly_expenses += total_paid
        self.cash_balance -= total_paid
    
    def pay_debt_interest(self) -> None:
        """Maksa korko olemassa olevalle valtion velalle."""
        if self.total_debt <= 0:
            return
        
        monthly_interest_rate = self.debt_interest_rate_annual / 12.0
        interest_payment = self.total_debt * monthly_interest_rate
        
        self.debt_service_expenses = interest_payment
        self.monthly_expenses += interest_payment
        self.cash_balance -= interest_payment
    
    def make_public_purchases(self) -> None:
        """Tee julkisia hankintoja yrityksiltä.
        
        Simuloi valtion ostoja (terveydenhuolto, koulutus, infrastruktuuri).
        Palauttaa rahaa talouteen ja tukee yritysten kysyntää.
        """
        # Lasketaan ostobudjetti tulojen perusteella
        if self.monthly_revenue <= 0:
            return
        
        budget = self.monthly_revenue * self.public_spending_share
        
        if budget <= 0 or not self.model.firms:
            return
        
        # Jaa ostot tasaisesti kaikkien manufacturer-yritysten kesken
        manufacturers = [
            f for f in self.model.firms
            if f.alive and f.firm_type == "manufacturer"
        ]
        
        if not manufacturers:
            return
        
        per_firm = budget / len(manufacturers)
        total_spent = 0.0
        
        for firm in manufacturers:
            # Osta hyödykkeitä firmalta
            units = per_firm / firm.price
            if units > 0:
                revenue = firm.sell_goods(units)
                total_spent += revenue
        
        self.public_procurement_expenses = total_spent
        self.monthly_expenses += total_spent
        self.cash_balance -= total_spent
    
    # ==================== BUDJETTI JA VELKA ====================
    
    def run_budget(self) -> None:
        """Laske budjetin tulos ja päivitä velka kuukauden lopussa."""
        surplus = self.monthly_revenue - self.monthly_expenses
        
        # Jos alijäämä ja kassa menee negatiiviseksi → ota velkaa
        if self.cash_balance < 0:
            needed_loan = -self.cash_balance
            self.total_debt += needed_loan
            self.cash_balance = 0.0
    
    # ==================== JOHDETUT SUUREET ====================
    
    @property
    def monthly_surplus(self) -> float:
        """Kuukauden ylijäämä/alijäämä."""
        return self.monthly_revenue - self.monthly_expenses
    
    @property
    def debt_to_gdp_ratio(self) -> float:
        """Velka/BKT-suhde (arvio)."""
        # BKT-proxy: kuukausittainen kokonaiskulutus * 12
        gdp_proxy = self.model.total_consumption * 12
        if gdp_proxy <= 0:
            return 0.0
        return self.total_debt / gdp_proxy
    
    @property
    def effective_tax_rate(self) -> float:
        """Tosiasiallinen veroaste (verotulot / BKT-proxy)."""
        gdp_proxy = self.model.total_consumption * 12
        if gdp_proxy <= 0:
            return 0.0
        tax_revenue = self.income_tax_revenue + self.corporate_tax_revenue + self.vat_revenue
        return tax_revenue / (gdp_proxy / 12)
    
    def step(self) -> None:
        """Valtion kuukausisykli.
        
        HUOM: Tämä kutsutaan EconomyModel.step():stä oikeassa järjestyksessä.
        Ei käytä perinteistä agent.step()-mallia vaan pilkottuja metodeja.
        """
        # Tätä ei käytetä suoraan, vaan model.step() kutsuu yksittäisiä metodeja
        pass
