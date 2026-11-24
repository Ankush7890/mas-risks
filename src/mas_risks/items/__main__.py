"""Print generated items for reading by eye.

    python -m mas_risks.items --family leave_policy --n 10
    python -m mas_risks.items --n 2            # two items of every family
"""

import argparse

from . import FAMILIES, VERSIONS, generate
from .core import ROLES


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--family", choices=FAMILIES, help="default: all families")
    parser.add_argument("--seed", type=int, default=0, help="first seed")
    parser.add_argument("--n", type=int, default=1, help="number of consecutive seeds")
    args = parser.parse_args()

    for family in [args.family] if args.family else FAMILIES:
        for seed in range(args.seed, args.seed + args.n):
            item = generate(family, seed)
            print("=" * 100)
            print(f"{item.item_id}\n")
            print(item.render_turn1())
            print()
            for version in VERSIONS:
                print(f"[{version}] §{item.withheld_section_number} "
                      f"{item.withheld_section(version)}  -> correct: {item.correct_label(version)}")
            print("roles: " + ", ".join(f"{r}={item.label(r)}" for r in ROLES))
            print(f"valid argument (default_wrong only): {item.valid_reasoning}")
            print(f"misleading argument: {item.misleading_reasoning}")


if __name__ == "__main__":
    main()
