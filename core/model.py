from __future__ import annotations

from typing import Any

from mesa import Model
from mesa.datacollection import DataCollector

from agents.bank import BankAgent
from agents.household import HouseholdAgent
from agents.firm import FirmAgent
from agents.state import StateAgent


class EconomyModel(Model):
    """Yksinkertainen makrotason talousmalli v0.1.

    - Kuukausiaika-askel
    - Kotitaloudet, yritykset ja valtio
    - Palkat, verot, tulonsiirrot ja kulutus
    """

    def __init__(
        self,
        config: dict[str, Any],
        seed: int | None = None,
    ) -> None:
        super().__init__(seed=seed)

        self.month: int = 0
        self.total_consumption: float = 0.0  # Joka step resetoidaan

        agents_cfg = config.get("agents", {})
        households_cfg = config.get("households", {})
        wages_cfg = config.get("wages", {})
        taxes_cfg = config.get("taxes", {})
        transfers_cfg = config.get("transfers", {})
        banking_cfg = config.get("banking", {})
        firms_cfg = config.get("firms", {})

        n_households: int = int(agents_cfg.get("households", 100))
        n_firms: int = int(agents_cfg.get("firms", 3))
        initial_wage: float = float(wages_cfg.get("initial", 2500.0))
        initial_cash: float = float(households_cfg.get("initial_cash", 5000.0))
        propensity_to_consume: float = float(households_cfg.get("propensity_to_consume", 0.8))
        initial_age_min: int = int(households_cfg.get("initial_age_min", 20))
        initial_age_max: int = int(households_cfg.get("initial_age_max", 65))

        cash_floor_default = initial_cash * 0.2
        cash_target_default = max(initial_cash * 0.5, cash_floor_default + 1.0)
        self.household_cash_floor: float = float(
            households_cfg.get("cash_floor", cash_floor_default)
        )
        self.household_cash_target: float = float(
            households_cfg.get("cash_target", cash_target_default)
        )
        self.household_debt_service_income_share: float = float(
            households_cfg.get("debt_service_income_share", 0.25)
        )
        self.household_debt_service_buffer_multiplier: float = float(
            households_cfg.get("debt_service_buffer_multiplier", 1.1)
        )

        self.retirement_age: int = int(households_cfg.get("retirement_age", 65))
        self.max_age: int = int(households_cfg.get("max_age", 90))
        self.death_prob_per_year: float = float(households_cfg.get("death_prob_per_year", 0.01))
        self.birth_rate_per_year: float = float(households_cfg.get("birth_rate_per_year", 0.015))
        self.fertile_age_min: int = int(households_cfg.get("fertile_age_min", 20))
        self.fertile_age_max: int = int(households_cfg.get("fertile_age_max", 45))
        self.child_initial_cash: float = float(households_cfg.get("child_initial_cash", 0.0))

        self.tax_rate: float = float(taxes_cfg.get("income_flat_rate", 0.25))
        self.vat_rate: float = float(taxes_cfg.get("vat_rate", 0.24))
        self.unemployment_benefit: float = float(
            transfers_cfg.get("unemployment_benefit", 1200.0)
        )
        self.pension: float = float(transfers_cfg.get("pension", 1500.0))

        firm_investment_interval = int(firms_cfg.get("investment_interval_months", 12))
        firm_investment_amount = float(firms_cfg.get("investment_loan_amount", 50000.0))
        firm_investment_term = int(firms_cfg.get("investment_loan_term", 48))
        firm_investment_cash_buffer = float(firms_cfg.get("investment_cash_buffer", 0.0))

        # Luodaan valtio-agentti (Mesa 3.x rekisteröi agentit automaattisesti)
        self.state = StateAgent(
            model=self,
        )

        # Luodaan yritykset
        self.firms: list[FirmAgent] = []
        for i in range(n_firms):
            firm = FirmAgent(
                model=self,
                wage_level=initial_wage,
                investment_interval_months=firm_investment_interval,
                investment_loan_amount=firm_investment_amount,
                investment_loan_term=firm_investment_term,
                investment_cash_buffer=firm_investment_cash_buffer,
            )
            self.firms.append(firm)

        # Luodaan kotitaloudet satunnaisilla iäillä
        self.households: list[HouseholdAgent] = []
        for i in range(n_households):
            age = self.random.randint(initial_age_min, initial_age_max)
            household = HouseholdAgent(
                model=self,
                age=age,
                initial_cash=initial_cash,
                propensity=propensity_to_consume,
            )
            self.households.append(household)

        # Luodaan pankki, joka hallinnoi luottoja ja talletuksia
        self.bank: BankAgent = BankAgent(
            model=self,
            config=banking_cfg,
        )

        self.datacollector = DataCollector(
            model_reporters={
                "month": lambda m: m.month,
                "unemployment_rate": lambda m: m.unemployment_rate,
                "state_balance": lambda m: m.state_balance,
                "total_consumption": lambda m: m.total_consumption,
                "gini_wealth": lambda m: m.gini_wealth,
                "avg_age": lambda m: sum(h.age for h in m.households if h.alive) / max(1, sum(1 for h in m.households if h.alive)),
                "population": lambda m: sum(1 for h in m.households if h.alive),
                "money_supply_m1": lambda m: m.money_supply_m1,
                "bank_total_loans": lambda m: m.bank_total_loans,
                "bank_capital_ratio": lambda m: m.bank_capital_ratio,
                "bank_default_losses": lambda m: getattr(m.bank, "total_defaulted", 0.0),
                "bank_performing_share": lambda m: m.bank_performing_share,
                "bank_age_bucket_0_6": lambda m: m.bank_age_bucket_0_6,
                "bank_age_bucket_6_12": lambda m: m.bank_age_bucket_6_12,
                "bank_age_bucket_12_24": lambda m: m.bank_age_bucket_12_24,
                "bank_age_bucket_24_plus": lambda m: m.bank_age_bucket_24_plus,
                "bank_investment_loan_share": lambda m: m.bank_investment_loan_share,
                "bank_nonperforming_balance": lambda m: m.bank_nonperforming_balance,
                "bank_avg_active_loan_age": lambda m: m.bank_avg_active_loan_age,
            },
            agent_reporters={
                "cash": "cash",
                "net_worth": lambda a: getattr(a, "net_worth", 0.0),
                "age": lambda a: getattr(a, "age", None),
                "alive": lambda a: getattr(a, "alive", None),
                "employed": lambda a: getattr(a, "employed", None),
            },
        )

    # --- Johdetut suureet ---
    @property
    def unemployment_rate(self) -> float:
        households = [h for h in self.households]
        if not households:
            return 0.0
        unemployed = sum(1 for h in households if not h.employed)
        return unemployed / len(households)

    @property
    def state_balance(self) -> float:
        return self.state.cash_balance

    @property
    def gini_wealth(self) -> float:
        from output.metrics import gini_coefficient
        # v0.2: käytetään nettovarallisuutta (net_worth) pelkän käteisen sijaan
        wealths = [hh.net_worth for hh in self.households if hh.alive]
        return gini_coefficient(wealths)

    @property
    def money_supply_m1(self) -> float:
        return self.bank.money_supply

    @property
    def bank_total_loans(self) -> float:
        return self.bank.total_loans

    @property
    def bank_capital_ratio(self) -> float:
        return self.bank.capital_ratio

    @property
    def bank_performing_share(self) -> float:
        return self.bank.loan_metrics.get("performing_share", 0.0)

    @property
    def bank_age_bucket_0_6(self) -> float:
        return self.bank.loan_metrics.get("age_bucket_0_6_share", 0.0)

    @property
    def bank_age_bucket_6_12(self) -> float:
        return self.bank.loan_metrics.get("age_bucket_6_12_share", 0.0)

    @property
    def bank_age_bucket_12_24(self) -> float:
        return self.bank.loan_metrics.get("age_bucket_12_24_share", 0.0)

    @property
    def bank_age_bucket_24_plus(self) -> float:
        return self.bank.loan_metrics.get("age_bucket_24_plus_share", 0.0)

    @property
    def bank_investment_loan_share(self) -> float:
        return self.bank.loan_metrics.get("purpose_investment_share", 0.0)

    @property
    def bank_nonperforming_balance(self) -> float:
        return self.bank.loan_metrics.get("nonperforming_balance", 0.0)

    @property
    def bank_avg_active_loan_age(self) -> float:
        return self.bank.loan_metrics.get("avg_active_age", 0.0)

    # --- Syntyvyys ---
    def process_births(self) -> None:
        """Käsittele syntyvyys kuukausittain.
        
        Syntyvyysaste voi olla vakio tai dynaaminen (tulevissa versioissa).
        Lasketaan hedelmällisessä iässä olevat agentit ja synnytetään uusia.
        """
        living_households = [h for h in self.households if h.alive]
        fertile_households = [
            h for h in living_households 
            if self.fertile_age_min <= h.age <= self.fertile_age_max
        ]
        
        if not fertile_households:
            return
        
        # Kuukausittainen syntymätodennäköisyys per hedelmällinen agentti
        monthly_birth_prob = self.birth_rate_per_year / 12
        
        # Dynaaminen syntyvyys (jos halutaan säätää ajan mukaan)
        # Esim. voidaan lisätä: monthly_birth_prob *= self.birth_rate_multiplier()
        
        for parent in fertile_households:
            if self.random.random() < monthly_birth_prob:
                # Syntyy uusi agentti
                child = HouseholdAgent(
                    model=self,
                    age=0,
                    initial_cash=self.child_initial_cash,
                    propensity=parent.base_propensity_to_consume,
                )
                self.households.append(child)
                if self.child_initial_cash > 0 and hasattr(self, "bank"):
                    self.bank.record_new_deposit(self.child_initial_cash)
    
    def birth_rate_multiplier(self) -> float:
        """Dynaaminen syntyvyyskerroin (valinnainen).
        
        Voidaan säätää ajan, taloudellisen tilanteen tai muiden tekijöiden mukaan.
        Esim:
        - Laskeva trendi: return 1.0 - (self.month / 10000)
        - Taloussuhdanne: return 1.0 + 0.3 * (self.state_balance / 1e7)
        """
        # v0.2: vakio, mutta voidaan laajentaa myöhemmin
        return 1.0

    # --- Kuukausisykli ---
    def step(self) -> None:
        """Yksi kuukausi.

        1. Yritykset maksavat palkat (brutto)
        2. Valtio kerää tuloveron palkoista
        3. Valtio maksaa tuet ja eläkkeet
        4. Kotitaloudet kuluttavat osan tuloistaan yritysten tuotteisiin
        5. Kulutus → yritysten liikevaihto (+ ALV valtiolle)
        """

        self.month += 1
        self.total_consumption = 0.0

        # Järjestys: valtio → yritykset → pankki → kotitaloudet
        self.state.step()
        for firm in self.firms:
            firm.step()
        for hh in self.households:
            hh.step()

        # Kulutus → yritysten liikevaihto (+ ALV valtiolle)
        if self.total_consumption > 0 and len(self.firms) > 0:
            # Jaa kulutus tasaisesti yrityksille (v0.1 yksinkertaistus)
            consumption_per_firm = self.total_consumption / len(self.firms)
            vat_amount = consumption_per_firm * self.vat_rate
            net_revenue = consumption_per_firm - vat_amount

            for firm in self.firms:
                firm.receive_revenue(net_revenue)
            # Valtio kerää ALV:n
            self.state.cash_balance += vat_amount * len(self.firms)

        # Pankki hoitaa lainojen kassavirrat kuukauden lopussa
        self.bank.step()

        # Kerätään data tämän kuukauden lopussa
        self.datacollector.collect(self)

    def run_for_months(self, n_months: int) -> None:
        for _ in range(n_months):
            self.step()

    def get_results(self) -> dict[str, Any]:
        """Palauta yksinkertainen tulosdict v0.1-käyttöön."""

        model_df = self.datacollector.get_model_vars_dataframe()
        agent_df = self.datacollector.get_agent_vars_dataframe()
        return {"model": model_df, "agents": agent_df}
