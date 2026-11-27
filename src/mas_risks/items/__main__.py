"""Print generated items for reading by eye.

    python -m mas_risks.items --family leave_policy --n 10
    python -m mas_risks.items --n 2            # two items of every family
"""

import argparse

from . import ALL_FAMILIES, generate
from .core import ROLES


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--family", choices=ALL_FAMILIES, help="default: all families")
    parser.add_argument("--seed", type=int, default=0, help="first seed")
    parser.add_argument("--n", type=int, default=1, help="number of consecutive seeds")
    args = parser.parse_args()

    for family in [args.family] if args.family else ALL_FAMILIES:
        for seed in range(args.seed, args.seed + args.n):
            item = generate(family, seed)
            print("=" * 100)
            print(f"{item.item_id}\n")
            print(item.render_turn1())
            print()
            for version in item.versions:
                print(f"[{version}] §{item.withheld_section_number} "
                      f"{item.withheld_section(version)}  -> correct: {item.correct_label(version)}")
            print("roles: " + ", ".join(f"{r}={item.label(r)}" for r in ROLES))
            print(f"rule argument ({'sound' if item.rule_applies else 'unsound: condition not met'}), "
                  f"for {item.label('changed')}: {item.rule_reasoning}")
            print(f"mistake behind the distractor: {item.distractor_reasoning}")


if __name__ == "__main__":
    main()
