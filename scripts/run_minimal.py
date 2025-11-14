from __future__ import annotations

from core.config import load_config
from core.model import EconomyModel


def main() -> None:
    cfg = load_config("config/base.yaml")
    n_months = cfg.get("simulation", {}).get("months", 120)

    model = EconomyModel(
        config=cfg,
        seed=42,
    )

    print(f"Aloitetaan {n_months} kuukauden simulaatio...")
    model.run_for_months(n_months)
    results = model.get_results()
    model_df = results["model"]

    print("\n=== Viimeinen kuukausi ===")
    last = model_df.iloc[-1]
    print(f"Kuukausi: {int(last['month'])}")
    print(f"CPI: {last['cpi']:.4f} (aloitus: {model_df.iloc[0]['cpi']:.4f})")  # v0.4: UUSI
    print(f"Väestö: {int(last['population'])} (aloitus: {int(model_df.iloc[0]['population'])})")
    print(f"Työttömyysaste: {last['unemployment_rate']:.1%}")
    print(f"Keski-ikä: {last['avg_age']:.1f} vuotta")
    print(f"Valtion saldo: {last['state_balance']:,.0f} €")
    print(f"Kokonaiskulutus: {last['total_consumption']:,.0f} €")
    print(f"Gini (varallisuus): {last['gini_wealth']:.3f}")
    print(f"Rahamäärä M1: {last['money_supply_m1']:,.0f} €")
    print(f"Pankin luottokanta: {last['bank_total_loans']:,.0f} €")
    print(f"Pankin pääomasuhde: {last['bank_capital_ratio']:.2%}")
    print(f"Performoiva luottosuhde: {last['bank_performing_share']:.2%}")
    print(f"Investointilainojen osuus: {last['bank_investment_loan_share']:.2%}")
    print(f"Aktiivisten lainojen keski-ikä: {last['bank_avg_active_loan_age']:.1f} kk")

    print("\n=== Keskiarvot koko ajalta ===")
    print(f"Väestön keskikoko: {model_df['population'].mean():.0f}")
    print(f"CPI (ka): {model_df['cpi'].mean():.4f}")
    print(f"CPI volatiliteetti (std): {model_df['cpi'].std():.4f}")
    print(f"Keskityöttömyys: {model_df['unemployment_rate'].mean():.1%}")
    print(f"Keski-ikä (ka): {model_df['avg_age'].mean():.1f} vuotta")
    print(f"Gini (ka): {model_df['gini_wealth'].mean():.3f}")
    print(f"M1 (ka): {model_df['money_supply_m1'].mean():,.0f} €")
    print(f"Pankin luottokanta (ka): {model_df['bank_total_loans'].mean():,.0f} €")
    print(f"Performoiva luottosuhde (ka): {model_df['bank_performing_share'].mean():.2%}")
    
    print("\n=== Asuntomarkkina (v0.5) ===")
    print(f"Kotitalouden keskikoko: {model_df['avg_household_size'].mean():.2f} hlö")
    print(f"Asukasta per asunto: {model_df['residents_per_dwelling'].mean():.2f} hlö/asunto")
    print(f"Omistusasumisen aste: {model_df['housing_ownership_rate'].mean():.1%}")
    print(f"Asuntojen keskihinta: {model_df['avg_house_price'].mean():,.0f} €")
    print(f"  - Yksiöt (ka): {model_df['avg_house_price_size_1'].mean():,.0f} €")
    print(f"  - Kaksiot (ka): {model_df['avg_house_price_size_2'].mean():,.0f} €")
    print(f"  - Kolmiot (ka): {model_df['avg_house_price_size_3'].mean():,.0f} €")
    print(f"  - Neliöt+ (ka): {model_df['avg_house_price_size_4'].mean():,.0f} €")
    print(f"Kauppoja per kuukausi (ka): {model_df['housing_transactions'].mean():.1f}")
    
    print("\n=== Yrittäjyys (v0.6) ===")
    print(f"Yrittäjyysaste: {last['entrepreneurship_rate']:.1%}")
    print(f"Aktiivisia yrityksiä: {int(last['num_active_firms'])}")
    print(f"Uusia yrityksiä/kk (ka): {model_df['firm_births_per_month'].mean():.2f}")
    print(f"Konkursseja/kk (ka): {model_df['firm_deaths_per_month'].mean():.2f}")
    print(f"Yritysten keski-ikä: {last['avg_firm_age']:.1f} kk")
    print(f"Yrittäjien varallisuusosuus: {last['entrepreneur_wealth_share']:.1%}")
    
    print("\n=== Rakennusala (v0.7) ===")
    print(f"Aktiivisia projekteja: {int(last['construction_projects_active'])}")
    print(f"Rakennusalan työpaikat: {int(last['construction_employment'])}")
    print(f"Valmistuneita asuntoja/kk (ka): {model_df['dwellings_completed_per_month'].mean():.2f}")
    print(f"Rakennusliikkeiden kassa: {last['construction_sector_cash']:,.0f} €")
    print(f"Keskimääräinen voittomarginaali: {last['avg_construction_profit_margin']:.1%}")
    
    print("\n=== Valtio (v0.8) ===")
    print(f"Kuukausitulot: {last['state_monthly_revenue']:,.0f} €")
    print(f"  - Tulovero: {last['state_income_tax']:,.0f} € ({last['state_income_tax']/last['state_monthly_revenue']*100:.1f}%)")
    print(f"  - Yhteisövero: {last['state_corporate_tax']:,.0f} € ({last['state_corporate_tax']/last['state_monthly_revenue']*100:.1f}%)")
    print(f"  - ALV: {last['state_vat']:,.0f} € ({last['state_vat']/last['state_monthly_revenue']*100:.1f}%)")
    print(f"  - Myyntivoittovero: {last['state_capital_gains_tax']:,.0f} €")
    print(f"Kuukausimmenot: {last['state_monthly_expenses']:,.0f} €")
    print(f"  - Tuet: {last['state_transfers']:,.0f} €")
    print(f"  - Velanhoito: {last['state_debt_service']:,.0f} €")
    print(f"  - Julkiset hankinnat: {last['state_public_procurement']:,.0f} €")
    print(f"Ylijäämä/alijäämä: {last['state_surplus']:,.0f} €")
    print(f"Valtion velka: {last['state_total_debt']:,.0f} €")
    print(f"Velka suhteessa BKT:hen: {last['state_debt_to_gdp']:.1%}")
    print(f"Efektiivinen veroprosentti: {last['effective_tax_rate']:.1%}")


if __name__ == "__main__":
    main()
