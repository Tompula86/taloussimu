from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from core.config import load_config
from core.model import EconomyModel


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Aja taloussimulaatio annetulla konfiguraatiolla."
    )
    parser.add_argument(
        "--config",
        type=str,
        default="config/base.yaml",
        help="Polku konfiguraatiotiedostoon (oletus: config/base.yaml)",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Polku tulosten tallennukseen CSV-muodossa (oletus: ei tallenneta)",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Satunnaissiemen (oletus: 42)",
    )

    args = parser.parse_args()

    cfg = load_config(args.config)
    n_months = cfg.get("simulation", {}).get("months", 120)

    print(f"Konfiguraatio: {args.config}")
    print(f"Siemen: {args.seed}")
    print(f"Simulaation pituus: {n_months} kuukautta\n")

    model = EconomyModel(config=cfg, seed=args.seed)
    model.run_for_months(n_months)
    results = model.get_results()
    model_df = results["model"]

    print("\n=== Simulaatio valmis ===")
    last = model_df.iloc[-1]
    print(f"Viimeinen kuukausi: {int(last['month'])}")
    print(f"Työttömyysaste: {last['unemployment_rate']:.1%}")
    print(f"Gini (varallisuus): {last['gini_wealth']:.3f}")
    print(f"Valtion saldo: {last['state_balance']:,.0f} €")

    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        model_df.to_csv(output_path, index=False)
        print(f"\nTulokset tallennettu: {output_path}")


if __name__ == "__main__":
    main()