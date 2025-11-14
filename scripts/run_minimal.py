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
    print(f"Keskityöttömyys: {model_df['unemployment_rate'].mean():.1%}")
    print(f"Keski-ikä (ka): {model_df['avg_age'].mean():.1f} vuotta")
    print(f"Gini (ka): {model_df['gini_wealth'].mean():.3f}")
    print(f"M1 (ka): {model_df['money_supply_m1'].mean():,.0f} €")
    print(f"Pankin luottokanta (ka): {model_df['bank_total_loans'].mean():,.0f} €")
    print(f"Performoiva luottosuhde (ka): {model_df['bank_performing_share'].mean():.2%}")


if __name__ == "__main__":
    main()
