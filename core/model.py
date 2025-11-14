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
        # v0.7: 1 rakennusliike + loput valmistajia
        self.firms: list[FirmAgent] = []
        
        # Luo 1 rakennusliike
        construction_firm = FirmAgent(
            model=self,
            wage_level=initial_wage * 1.1,  # Hieman korkeampi palkka rakennusalalla
            investment_interval_months=0,  # Ei tavallisia investointeja
            investment_loan_amount=0,
            investment_loan_term=1,
            investment_cash_buffer=0.0,
            firm_type="construction",
        )
        self.firms.append(construction_firm)
        
        # Luo loput valmistajiksi
        for i in range(n_firms - 1):
            firm = FirmAgent(
                model=self,
                wage_level=initial_wage,
                investment_interval_months=firm_investment_interval,
                investment_loan_amount=firm_investment_amount,
                investment_loan_term=firm_investment_term,
                investment_cash_buffer=firm_investment_cash_buffer,
                firm_type="manufacturer",
            )
            self.firms.append(firm)

        # Luodaan kotitaloudet satunnaisilla iäillä
        self.households: list[HouseholdAgent] = []
        for i in range(n_households):
            age = self.random.randint(initial_age_min, initial_age_max)
            # v0.5: Alustetaan household_size realistisesti iän mukaan
            if age < 25:
                household_size = 1  # Nuoret yksin
            elif age < 35:
                household_size = self.random.choice([1, 2, 2])  # Pääosin pareja
            elif age < 50:
                household_size = self.random.choice([2, 3, 4, 4])  # Perheitä
            else:
                household_size = self.random.choice([1, 2, 2])  # Vanhemmat pareja tai yksin
            
            household = HouseholdAgent(
                model=self,
                age=age,
                initial_cash=initial_cash,
                propensity=propensity_to_consume,
                household_size=household_size,
            )
            self.households.append(household)

        # v0.7: Alusta työllisyys jakamalla työikäiset kotitaloudet tasaisesti firmoille
        if self.firms:
            for i, hh in enumerate(self.households):
                if hh.age < self.retirement_age and hh.alive:
                    firm = self.firms[i % len(self.firms)]
                    hh.employed = True
                    hh.employer = firm
                    hh.wage = firm.wage_level
                    firm.employees.append(hh)

            # Aseta tavoitetyöntekijämäärät alkuperäisen tilanteen mukaan
            for firm in self.firms:
                firm.target_employees = len(firm.employees)

        # Luodaan pankki, joka hallinnoi luottoja ja talletuksia
        self.bank: BankAgent = BankAgent(
            model=self,
            config=banking_cfg,
        )
        
        # v0.5: Luodaan asuntomarkkina
        from markets.housing import HousingMarket
        housing_cfg = config.get("housing", {})
        self.leaving_home_rate_per_month: float = float(
            housing_cfg.get("leaving_home_rate_per_month", 0.01)
        )
        self.housing_market = HousingMarket(model=self)
        
        # v0.6: Yrittäjyys-konfiguraatio
        entrepreneurship_cfg = config.get("entrepreneurship", {})
        self.entrepreneurship_rate_per_month: float = float(
            entrepreneurship_cfg.get("rate_per_month", 0.001)
        )
        self.firm_seed_capital: float = float(
            entrepreneurship_cfg.get("firm_seed_capital", 10000.0)
        )
        self.entrepreneur_cash_buffer: float = float(
            entrepreneurship_cfg.get("entrepreneur_cash_buffer", 5000.0)
        )
        self.startup_business_loan: float = float(
            entrepreneurship_cfg.get("startup_business_loan", 30000.0)
        )
        # Alusta asuntokanta (oletuksena 80% kotitalouksista)
        initial_dwellings = int(n_households * 0.8)
        self.housing_market.initialize_housing_stock(initial_dwellings)
        # Tallenna CPI-pohja asuntohintojen inflaatio-linkitykselle
        self.cpi_base = 1.0
        self.last_cpi = 1.0
        
        # Alusta osa kotitalouksista asunnonomistajiksi (60% omistusaste)
        self._initialize_housing_ownership()

        self.datacollector = DataCollector(
            model_reporters={
                "month": lambda m: m.month,
                "cpi": lambda m: m.cpi,  # v0.4: UUSI - Consumer Price Index
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
                # v0.5: Asuntomarkkina-mittarit
                "avg_household_size": lambda m: m.avg_household_size,
                "residents_per_dwelling": lambda m: m.residents_per_dwelling,
                "housing_ownership_rate": lambda m: m.housing_ownership_rate,
                "avg_house_price": lambda m: m.avg_house_price,
                "avg_house_price_size_1": lambda m: m.avg_house_price_by_size(1),
                "avg_house_price_size_2": lambda m: m.avg_house_price_by_size(2),
                "avg_house_price_size_3": lambda m: m.avg_house_price_by_size(3),
                "avg_house_price_size_4": lambda m: m.avg_house_price_by_size(4),
                "housing_transactions": lambda m: m.housing_market.monthly_transactions,
                # v0.6: Yrittäjyys-mittarit
                "entrepreneurship_rate": lambda m: m.entrepreneurship_rate,
                "firm_births_per_month": lambda m: m.firm_births_per_month,
                "firm_deaths_per_month": lambda m: m.firm_deaths_per_month,
                "avg_firm_age": lambda m: m.avg_firm_age,
                "entrepreneur_wealth_share": lambda m: m.entrepreneur_wealth_share,
                "num_active_firms": lambda m: m.num_active_firms,
                # v0.7: Rakennusliike-mittarit
                "construction_projects_active": lambda m: m.construction_projects_active,
                "construction_employment": lambda m: m.construction_employment,
                "dwellings_completed_per_month": lambda m: m.dwellings_completed_per_month,
                "construction_sector_cash": lambda m: m.construction_sector_cash,
                "avg_construction_profit_margin": lambda m: m.avg_construction_profit_margin,
            },
            agent_reporters={
                "cash": "cash",
                "net_worth": lambda a: getattr(a, "net_worth", 0.0),
                "age": lambda a: getattr(a, "age", None),
                "alive": lambda a: getattr(a, "alive", None),
                "employed": lambda a: getattr(a, "employed", None),
                "household_size": lambda a: getattr(a, "household_size", None),
            },
        )

    def _initialize_housing_ownership(self) -> None:
        """v0.5: Alusta osa kotitalouksista asunnonomistajiksi.
        
        Jaa asunnot kotitalouksille koon mukaan sopivasti.
        """
        # Järjestä kotitaloudet household_size mukaan (isoimmat ensin)
        sorted_households = sorted(
            [h for h in self.households if h.alive],
            key=lambda h: h.household_size,
            reverse=True,
        )
        
        # Järjestä asunnot koon mukaan (isoimmat ensin)
        sorted_dwellings = sorted(
            self.housing_market.dwellings,
            key=lambda d: d.size,
            reverse=True,
        )
        
        # Jaa asunnot kotitalouksille (60% saa asunnon)
        target_owners = int(len(sorted_households) * 0.6)
        for i, household in enumerate(sorted_households[:target_owners]):
            if i >= len(sorted_dwellings):
                break
            
            dwelling = sorted_dwellings[i]
            dwelling.owner = household
            dwelling.for_sale = False
            household.dwelling = dwelling
            # Ei velkaa alussa
    
    # --- Johdetut suureet ---
    @property
    def cpi(self) -> float:
        """v0.4: Consumer Price Index = yritysten hintojen keskiarvo.
        
        Mahdollistaa inflaation/deflaation seurannan.
        """
        if not self.firms:
            return 1.0
        return sum(f.price for f in self.firms) / len(self.firms)

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
    
    # v0.5: Asuntomarkkina-mittarit
    @property
    def avg_household_size(self) -> float:
        """Kotitalouden keskikoko."""
        alive = [h for h in self.households if h.alive]
        if not alive:
            return 0.0
        return sum(h.household_size for h in alive) / len(alive)
    
    @property
    def residents_per_dwelling(self) -> float:
        """Asukasta per asunto - vastaa käyttäjän kysymykseen!"""
        if not self.housing_market.dwellings:
            return 0.0
        total_residents = sum(h.household_size for h in self.households if h.alive)
        return total_residents / len(self.housing_market.dwellings)
    
    @property
    def housing_ownership_rate(self) -> float:
        """Omistusasumisen aste."""
        alive = [h for h in self.households if h.alive]
        if not alive:
            return 0.0
        owners = len([h for h in alive if h.dwelling is not None])
        return owners / len(alive)
    
    @property
    def avg_house_price(self) -> float:
        """Asuntojen keskihinta."""
        if not self.housing_market.dwellings:
            return 0.0
        return sum(d.market_value for d in self.housing_market.dwellings) / len(self.housing_market.dwellings)
    
    def avg_house_price_by_size(self, size: int) -> float:
        """Asuntojen keskihinta koon mukaan."""
        size_dwellings = [d for d in self.housing_market.dwellings if d.size == size]
        if not size_dwellings:
            return 0.0
        return sum(d.market_value for d in size_dwellings) / len(size_dwellings)
    
    # v0.6: Yrittäjyys-mittarit
    @property
    def entrepreneurship_rate(self) -> float:
        """Yrittäjien osuus työvoimasta."""
        alive = [h for h in self.households if h.alive]
        if not alive:
            return 0.0
        entrepreneurs = len([h for h in alive if h.entrepreneur])
        return entrepreneurs / len(alive)
    
    @property
    def firm_births_per_month(self) -> float:
        """Uusien yritysten määrä kuukaudessa."""
        if self.month == 0:
            return 0.0
        recent_startups = len([f for f in self.firms if f.is_startup and f.alive and self.month - f.founded_month <= 1])
        return recent_startups
    
    @property
    def firm_deaths_per_month(self) -> float:
        """Konkurssien määrä kuukaudessa."""
        if self.month == 0:
            return 0.0
        # Pysyvä laskuri tarvittaisiin - tämä on tilannekuva
        dead_firms = len([f for f in self.firms if not f.alive])
        return dead_firms / max(1, self.month)
    
    @property
    def avg_firm_age(self) -> float:
        """Yritysten keski-ikä kuukausissa."""
        alive_firms = [f for f in self.firms if f.alive]
        if not alive_firms:
            return 0.0
        ages = [max(0, self.month - f.founded_month) for f in alive_firms]
        return sum(ages) / len(ages) if ages else 0.0
    
    @property
    def entrepreneur_wealth_share(self) -> float:
        """Yrittäjien osuus kokonaisvarallisuudesta."""
        alive = [h for h in self.households if h.alive]
        if not alive:
            return 0.0
        
        total_wealth = sum(h.net_worth for h in alive)
        if total_wealth <= 0:
            return 0.0
        
        entrepreneur_wealth = sum(h.net_worth for h in alive if h.entrepreneur)
        return entrepreneur_wealth / total_wealth
    
    @property
    def num_active_firms(self) -> int:
        """Toiminnassa olevien yritysten määrä."""
        return len([f for f in self.firms if f.alive])
    
    # v0.7: Rakennusliike-mittarit
    @property
    def construction_projects_active(self) -> int:
        """Aktiivisten rakennusprojektien määrä."""
        construction_firms = [f for f in self.firms if f.alive and f.firm_type == "construction"]
        return sum(len([p for p in f.construction_projects if p.status == "ongoing"]) 
                  for f in construction_firms)
    
    @property
    def construction_employment(self) -> int:
        """Rakennusalan työpaikat."""
        construction_firms = [f for f in self.firms if f.alive and f.firm_type == "construction"]
        return sum(len(f.employees) for f in construction_firms)
    
    @property
    def dwellings_completed_per_month(self) -> int:
        """Valmistuneet asunnot kuukaudessa."""
        if self.month == 0:
            return 0
        construction_firms = [f for f in self.firms if f.alive and f.firm_type == "construction"]
        completed = sum(len([p for p in f.construction_projects if p.status == "completed" 
                            and self.month - p.start_month <= 1])
                       for f in construction_firms)
        return completed
    
    @property
    def construction_sector_cash(self) -> float:
        """Rakennusliikkeiden kassatilanne yhteensä."""
        construction_firms = [f for f in self.firms if f.alive and f.firm_type == "construction"]
        return sum(f.cash for f in construction_firms)
    
    @property
    def avg_construction_profit_margin(self) -> float:
        """Keskimääräinen rakennusalan voittomarginaali."""
        construction_firms = [f for f in self.firms if f.alive and f.firm_type == "construction"]
        if not construction_firms:
            return 0.0
        
        # Laskee keskimääräisen marginaalin aktiivisista projekteista
        # (arvioitu myyntihinta - käytetty budjetti) / käytetty budjetti
        total_margin = 0.0
        project_count = 0
        
        for firm in construction_firms:
            for project in firm.construction_projects:
                if project.spent_so_far > 0:
                    estimated_revenue = self.housing_market.avg_price_for_size(project.dwelling_size)
                    margin = (estimated_revenue - project.spent_so_far) / project.spent_so_far
                    total_margin += margin
                    project_count += 1
        
        return total_margin / project_count if project_count > 0 else 0.0

    # --- Syntyvyys ---
    def process_births(self) -> None:
        """v0.5: Käsittele syntyvyys kasvattamalla perheen kokoa.
        
        Lapsi EI ole erillinen agentti syntymästä, vaan kasvattaa
        vanhemman household_size ja num_children -lukuja.
        Lapsi "aktivoituu" agentiksi vasta check_leaving_home():ssa.
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
        monthly_birth_prob *= self.birth_rate_multiplier()
        
        for parent in fertile_households:
            if self.random.random() < monthly_birth_prob:
                # v0.5: Lapsi kasvattaa perheen kokoa, ei luo agenttia
                parent.household_size += 1
                parent.num_children += 1
                # Lapsi "aktivoituu" agentiksi vasta 18-25v iässä
    
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

        v0.4: Yksinkertaistettu - kulutus tapahtuu suoraan agenttien välillä.
        
        1. Yritykset tuottavat, päivittävät hinnat ja maksavat palkat (brutto)
        2. Valtio kerää tuloveron palkoista
        3. Valtio maksaa tuet ja eläkkeet
        4. Kotitaloudet kuluttavat ostamalla hyödykkeitä yrityksiltä dynaamiseen hintaan
           (ALV kerätään ostohetkellä HouseholdAgent.consume():ssa)
        5. Pankki hoitaa lainojen kassavirrat
        """

        self.month += 1
        self.total_consumption = 0.0

        # v0.7: Työmarkkinat ennen valtiota ja palkanmaksua
        self._run_labor_market()

        # Järjestys: valtio → yritykset → kotitaloudet → pankki
        self.state.step()
        for firm in self.firms:
            firm.step()
        for hh in self.households:
            hh.step()

        # v0.4: Kulutus ja ALV hoidetaan nyt HouseholdAgent.consume():ssa
        # POISTETTU vanha kulutuksen jako-logiikka
        
        # Pankki hoitaa lainojen kassavirrat kuukauden lopussa
        self.bank.step()
        
        # v0.5: Asuntomarkkina (hinnoittelu ja kaupankäynti)
        self.housing_market_step()
        
        # Syntyvyys
        self.process_births()

        # Kerätään data tämän kuukauden lopussa
        self.datacollector.collect(self)

    def _run_labor_market(self) -> None:
        """v0.7: Orkestroi työmarkkinoiden irtisanomiset ja rekrytoinnit."""

        from agents.firm import FirmAgent  # vain tyyppiviitteeksi

        # 1) Päivitä kaikkien firmojen työvoimakysyntä ja palkkataso
        for firm in self.firms:
            if firm.alive:
                firm._update_labor_demand()
                firm._update_wage_level()
        


        # 2) Irtisanomiset ylityöllisistä firmoista
        unemployed_pool: list["HouseholdAgent"] = []
        for firm in self.firms:
            if not firm.alive:
                continue

            if len(firm.employees) > firm.target_employees:
                num_to_fire = len(firm.employees) - firm.target_employees
                if num_to_fire <= 0:
                    continue
                fired = self.random.sample(firm.employees, num_to_fire)
                for employee in fired:
                    employee.lose_job()
                    if employee in firm.employees:
                        firm.employees.remove(employee)
                    unemployed_pool.append(employee)

        # 3) Kerää kaikki työttömät työnhakijat
        for hh in self.households:
            if hh.alive and not hh.employed and hh not in unemployed_pool:
                unemployed_pool.append(hh)

        self.random.shuffle(unemployed_pool)

        # 4) Luo avoimet työpaikat firmojen target_employees-tavoitteiden perusteella
        vacancies: list[tuple[FirmAgent, float]] = []
        for firm in self.firms:
            if not firm.alive:
                continue
            num_vacancies = firm.target_employees - len(firm.employees)
            for _ in range(max(0, num_vacancies)):
                vacancies.append((firm, firm.wage_level))

        # Korkeapalkkaiset paikat täytetään ensin
        vacancies.sort(key=lambda x: x[1], reverse=True)

        # 5) Matching: työttömät täyttävät avoimia paikkoja
        for job_seeker in unemployed_pool:
            if not vacancies:
                break
            firm, wage = vacancies.pop(0)
            job_seeker.employed = True
            job_seeker.employer = firm
            job_seeker.wage = wage
            firm.employees.append(job_seeker)
    
    def housing_market_step(self) -> None:
        """v0.5: Asuntomarkkinan kuukausittainen päivitys.
        
        1. Päivitä hinnat (segmentoituna kokojen mukaan)
        2. Suorita kaupankäynti
        3. v0.7: Rakentaminen hoidetaan nyt construction-firmojen kautta
        """
        # Tallenna CPI kuukausittaista muutosta varten
        self.last_cpi = self.cpi
        
        self.housing_market.update_prices()
        self.housing_market.execute_transactions()
        # v0.7: Poistettu - rakentaminen hoidetaan nyt firmojen kautta
        # self.housing_market.consider_new_construction()

    def run_for_months(self, n_months: int) -> None:
        for _ in range(n_months):
            self.step()

    def get_results(self) -> dict[str, Any]:
        """Palauta yksinkertainen tulosdict v0.1-käyttöön."""

        model_df = self.datacollector.get_model_vars_dataframe()
        agent_df = self.datacollector.get_agent_vars_dataframe()
        return {"model": model_df, "agents": agent_df}
