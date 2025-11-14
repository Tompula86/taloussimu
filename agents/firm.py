from __future__ import annotations

from dataclasses import dataclass
from mesa import Agent


@dataclass
class ConstructionProject:
    """v0.7: Rakennusprojekti.
    
    Mallintaa yksittäisen asunnon rakentamisprosessia.
    """
    dwelling_size: int  # 1=yksiö, 2=kaksio, 3=kolmio, 4=neliö+
    start_month: int  # Milloin projekti aloitettiin
    duration_months: int  # Kuinka kauan rakentaminen kestää
    total_budget: float  # Alkuperäinen budjetti
    spent_so_far: float  # Paljonko on jo kulutettu
    status: str  # "ongoing", "completed", "delayed"
    workers_hired: int  # Montako työntekijää projektissa
    monthly_wage_budget: float  # Palkkamenot per kuukausi
    monthly_material_budget: float  # Materiaalikulut per kuukausi
    dwelling_id: int | None = None  # Valmiin asunnon ID
    completed_month: int | None = None  # v0.8.1: Milloin valmistui


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
        firm_type: str = "manufacturer",
    ) -> None:
        super().__init__(model)
        # v0.7: Yrityksen tyyppi
        self.firm_type: str = firm_type  # "manufacturer", "construction", "service"
        
        # v0.7: Yrityksen tarjoama palkkataso työpaikoille
        self.wage_level = wage_level
        # v0.7: Alkukassa palkanmaksuun ja käynnistykseen (6 kk palkkavaranto)
        initial_payroll_reserve = wage_level * 35 * 6  # ~35 työntekijää × 6 kk
        self.cash: float = initial_payroll_reserve if owner is None else initial_equity
        self.debt: float = 0.0
        self.capital_stock: float = 0.0
        self.investment_interval_months = max(0, investment_interval_months)
        self.investment_loan_amount = investment_loan_amount
        self.investment_loan_term = max(1, investment_loan_term)
        self.investment_cash_buffer = max(0.0, investment_cash_buffer)
        self.months_since_investment: int = 0
        
        # v0.4: Dynaaminen hinnoittelu ja varasto
        self.price: float = 30.0  # v0.7: Korkeampi aloitushinta (linkitetty palkkatasoon)
        self.inventory: float = 0.0  # v0.7: Aloitusvarasto nolla, tuotanto alkaa heti
        self.production_per_employee: float = 100.0  # v0.7: Työntekijäkohtainen tuotanto
        self.target_inventory: float = 1000.0  # v0.7: Korkeampi tavoitevarasto
        
        # v0.6: Yrittäjyys ja konkurssit
        self.owner = owner  # Viite HouseholdAgent:iin (jos yrittäjäyritys)
        self.equity: float = initial_equity  # Oma pääoma
        self.alive: bool = True  # Onko yritys toiminnassa
        self.founded_month: int = model.month  # Milloin perustettu
        self.is_startup: bool = owner is not None  # Onko uusi yrittäjäyritys
        # v0.7: Työvoima
        self.employees: list["HouseholdAgent"] = []
        self.target_employees: int = 0
        
        # v0.7: Rakennusliike-spesifit kentät
        if self.firm_type == "construction":
            self.construction_projects: list[ConstructionProject] = []
            self.construction_cost_per_sqm: float = 1200.0  # v0.8.1: Laskettu 2000 → 1200 €/m²
            self.construction_duration_months: int = 12
            self.target_profit_margin: float = 0.10  # v0.8.1: Laskettu 15% → 10%
            self.max_concurrent_projects: int = 3
        
        # v0.8: Kirjanpito (yritysveroa varten)
        self.revenue_this_month: float = 0.0
        self.expenses_this_month: float = 0.0

    def pay_wages(self) -> float:
        """v0.7: Maksa palkat vain omille työntekijöille.
        
        Jos yritys ei pysty maksamaan palkkoja, se menee konkurssiin.
        Tämä pakottaa yritykset tasapainottamaan työvoimansa tulojensa mukaan.
        """

        total_wages = 0.0
        for employee in list(self.employees):
            wage = getattr(employee, "wage", self.wage_level)
            if self.cash >= wage:
                self.cash -= wage
                employee.receive_income(wage)
                total_wages += wage
                self.expenses_this_month += wage  # v0.8: Kirjaa meno
            else:
                # Ei pysty maksamaan palkkoja → konkurssi
                self._go_bankrupt()
                return total_wages
        
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
        
        # v0.8: Nollaa kuukausittainen kirjanpito
        self.revenue_this_month = 0.0
        self.expenses_this_month = 0.0
        
        # v0.7: Työvoimapäätökset tehdään _run_labor_market():ssa ennen tätä
        self._produce()
        self._update_price()
        self._maybe_take_investment_loan()
        self.pay_wages()
        
        # v0.7: Rakennusliike-spesifi logiikka
        if self.firm_type == "construction":
            self._progress_construction_projects()
            self._consider_new_construction_project()
        
        self.check_bankruptcy()

    def _update_labor_demand(self) -> None:
        """v0.7: Päivitä tavoitetyöntekijämäärä.
        
        Manufacturers: Varastotilanteen mukaan
        Construction: Projektien mukaan
        """
        if self.firm_type == "construction":
            # Rakennusliike: työvoima projektien mukaan
            needed = sum(p.workers_hired for p in self.construction_projects if p.status == "ongoing")
            self.target_employees = needed
        else:
            # Manufacturer: varastotilanteen mukaan
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
        """v0.7: Tuotanto skaalautuu työntekijämäärän mukaan."""
        production = len(self.employees) * self.production_per_employee
        self.inventory += production

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
        self.revenue_this_month += revenue  # v0.8: Kirjaa tulo
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
    
    # v0.7: Rakennusliike-metodit
    
    def _consider_new_construction_project(self) -> None:
        """Vaihe 1: Markkina-analyysi ja projektin aloitus."""
        if self.firm_type != "construction":
            return
        
        if not self.alive:
            return
        
        # Tarkista onko kapasiteettia uudelle projektille
        if len(self.construction_projects) >= self.max_concurrent_projects:
            return
        
        # Analysoi markkinoita: mitkä asunnot kannattavat
        housing_market = self.model.housing_market
        
        best_size = None
        best_margin = 0.0
        
        for size in [1, 2, 3, 4]:
            # Laske keskihinta tälle koolle
            avg_price = housing_market.avg_price_for_size(size)
            if avg_price == 0:
                continue
            
            # Arvioi rakennuskustannus (koko vaikuttaa neliömäärään)
            sqm = 30 * size  # yksiö ~30m², kaksio ~60m², kolmio ~90m², neliö+ ~120m²
            construction_cost = sqm * self.construction_cost_per_sqm
            
            # Laske potentiaalinen voittomarginaali
            expected_margin = (avg_price - construction_cost) / construction_cost
            
            if expected_margin > best_margin:
                best_margin = expected_margin
                best_size = size
        
        # Kannattaako rakentaa? (tarvitaan vähintään tavoitemarginaali)
        if best_size is None or best_margin < self.target_profit_margin:
            return
        
        # Aloita uusi projekti
        self._start_construction_project(best_size)
    
    def _start_construction_project(self, dwelling_size: int) -> None:
        """Vaihe 2: Rahoitus ja projektin käynnistys."""
        if self.firm_type != "construction":
            return
        
        # Laske projektin budjetti
        sqm = 30 * dwelling_size
        total_cost = sqm * self.construction_cost_per_sqm
        
        # Jaa budjetti palkoiksi (50%) ja materiaaleiksi (50%)
        monthly_wage = (total_cost * 0.5) / self.construction_duration_months
        monthly_material = (total_cost * 0.5) / self.construction_duration_months
        
        # Tarvittavat työntekijät (oletetaan 3000€/kk palkka)
        workers_needed = int(monthly_wage / 3000.0) + 1
        
        # Hae rakennuslaina pankilta
        bank = getattr(self.model, "bank", None)
        if bank is None or bank.stop_lending:
            return
        
        # Tarkista onko yrityksellä tarpeeksi kassaa käynnistykseen (10% budjetista)
        if self.cash < total_cost * 0.1:
            return
        
        # Pyydä lainaa
        loan_approved = bank.request_loan(
            borrower=self,
            amount=total_cost,
            borrower_type="firm",
            term_months=self.construction_duration_months + 12,  # +1v lyhennyksille
            purpose="construction",
        )
        
        if not loan_approved:
            return
        
        # Luo uusi projekti
        project = ConstructionProject(
            dwelling_size=dwelling_size,
            start_month=self.model.month,
            duration_months=self.construction_duration_months,
            total_budget=total_cost,
            spent_so_far=0.0,
            status="ongoing",
            workers_hired=workers_needed,
            monthly_wage_budget=monthly_wage,
            monthly_material_budget=monthly_material,
        )
        
        self.construction_projects.append(project)
    
    def _progress_construction_projects(self) -> None:
        """Vaihe 3: Rakennusvaihe - kuukausittaiset kulut."""
        if self.firm_type != "construction":
            return
        
        for project in list(self.construction_projects):
            if project.status != "ongoing":
                continue
            
            # Tarkista onko projekti valmis
            months_elapsed = self.model.month - project.start_month
            if months_elapsed >= project.duration_months:
                self._complete_construction_project(project)
                continue
            
            # Maksa kuukausittaiset kulut
            monthly_cost = project.monthly_wage_budget + project.monthly_material_budget
            
            if self.cash >= monthly_cost:
                # Palkat: Luo työpaikkoja (v0.7: hoidetaan _run_labor_market():ssa)
                # Tässä vain kirjataan kulut
                self.cash -= project.monthly_wage_budget
                project.spent_so_far += project.monthly_wage_budget
                
                # Materiaalit: Ostetaan muilta yrityksiltä
                self._buy_construction_materials(project.monthly_material_budget)
                project.spent_so_far += project.monthly_material_budget
            else:
                # Ei rahaa → projekti viivästyy
                project.status = "delayed"
    
    def _buy_construction_materials(self, amount: float) -> None:
        """Osta rakennusmateriaaleja muilta yrityksiltä."""
        if amount <= 0:
            return
        
        # Jaa ostot tasaisesti kaikkien manufacturer-yritysten kesken
        manufacturers = [
            f for f in self.model.firms
            if f.alive and f.firm_type == "manufacturer"
        ]
        
        if not manufacturers:
            # Jos ei muita yrityksiä, raha vain katoaa (yksinkertaistus)
            self.cash -= amount
            return
        
        per_firm = amount / len(manufacturers)
        
        for firm in manufacturers:
            # Osta hyödykkeitä firmalta
            units = per_firm / firm.price
            firm.sell_goods(units)
    
    def _complete_construction_project(self, project: ConstructionProject) -> None:
        """Vaihe 4: Valmistuminen - luo uusi asunto."""
        if self.firm_type != "construction":
            return
        
        # Merkitse valmistumiskuukausi
        project.completed_month = self.model.month
        
        # Luo uusi Dwelling asuntomarkkinalle
        from markets.housing import Dwelling
        
        housing_market = self.model.housing_market
        
        # Laske asunnon perusarvo koon mukaan
        base_value_multipliers = {1: 1.0, 2: 1.5, 3: 2.0, 4: 2.5}
        base_value = housing_market.construction_cost_base * base_value_multipliers[project.dwelling_size]
        
        new_dwelling = Dwelling(
            dwelling_id=housing_market.next_id,
            size=project.dwelling_size,
            base_value=base_value,
            construction_year=self.model.month,
        )
        
        # v0.8: Tallenna todellinen rakennuskustannus myyntivoittoveroa varten
        new_dwelling.construction_cost = project.total_budget
        
        # Aseta markkinahinta nykyisen hintatason mukaan
        new_dwelling.market_value = housing_market.avg_price_for_size(project.dwelling_size)
        
        # Lisää asuntomarkkinalle ja aseta myyntiin
        housing_market.dwellings.append(new_dwelling)
        housing_market.next_id += 1
        new_dwelling.for_sale = True
        
        # Tallennetaan dwelling_id projektiin myyntiä varten
        project.dwelling_id = new_dwelling.id
        project.status = "completed"
        
        # Yritä myydä asunto heti (v0.7: yksinkertaistus)
        self._try_sell_completed_dwelling(project, new_dwelling)
    
    def _try_sell_completed_dwelling(self, project: ConstructionProject, dwelling) -> None:
        """Vaihe 5: Myynti ja tuloslaskelma.
        
        v0.8.1: Yksinkertaistetaan että asunto myydään välittömästi markkinahintaan.
        Tämä välttää rakennusliikkeen konkurssin odottaessa ostajia.
        Rahat tulevat "yleiseltä asuntomarkkinalta" (abstraktit ostajat).
        
        v0.8.1: Projekti SÄILYY listalla metriiikkoja varten (ei poisteta).
        """
        # ÄLÄ poista projektia - se tarvitaan metriikoille!
        
        # Myy asunto välittömästi markkinahintaan
        # (Simuloi ennakkomyyntiä tai välitöntä markkinoiden kysyntää)
        revenue = dwelling.market_value
        profit = revenue - project.spent_so_far
        
        # Lisää tulo kassaan JA kirjanpitoon
        self.cash += revenue
        self.revenue_this_month += revenue  # v0.8: Kirjanpito
