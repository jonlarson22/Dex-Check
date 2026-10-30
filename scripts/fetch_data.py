#!/usr/bin/env python3
"""
Fetch full Pokedex data from PokeAPI and merge it with the repo's pokemon.json.

Display names come from the existing pokemon.json (already curated); the BST
written out is the sum of the PokeAPI base stats (current generation, base
form), NOT the pokemon.json total. The original file's BSTs turned out to mix
generations (e.g. pre-Gen-7 stats for Dugtrio) and contain errors in many
Gen 9 entries (e.g. Pawmi was 290, actually 240), so API values win. The
script prints every disagreement as a warning for the record. Known form
notes: Minior = Meteor form, Terapagos = Normal form, Zacian/Zamazenta =
Hero form (the API defaults).

Output: data/pokemon_full.json
Run: python3 scripts/fetch_data.py
"""
import json
import sys
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "pokemon.json"
OUT = ROOT / "data" / "pokemon_full.json"

GEN_RANGES = [
    (1, 151, 1), (152, 251, 2), (252, 386, 3), (387, 493, 4), (494, 649, 5),
    (650, 721, 6), (722, 809, 7), (810, 905, 8), (906, 1025, 9),
]


def generation(dex: int) -> int:
    for lo, hi, gen in GEN_RANGES:
        if lo <= dex <= hi:
            return gen
    raise ValueError(dex)


def fetch(dex: int) -> dict:
    url = f"https://pokeapi.co/api/v2/pokemon/{dex}"
    req = urllib.request.Request(url, headers={"User-Agent": "Dex-Check data builder"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.load(resp)


def main() -> int:
    base = json.loads(SRC.read_text(encoding="utf-8"))
    base_by_dex = {int(p["dex"]): p for p in base}

    with ThreadPoolExecutor(max_workers=20) as pool:
        api_data = list(pool.map(fetch, sorted(base_by_dex)))

    enriched = []
    mismatches = []
    for raw in api_data:
        dex = raw["id"]
        src = base_by_dex[dex]
        stats = {s["stat"]["name"]: s["base_stat"] for s in raw["stats"]}
        api_bst = sum(stats.values())
        if api_bst != int(src["bst"]):
            mismatches.append((dex, src["name"], src["bst"], api_bst))

        height_m = raw["height"] / 10.0            # decimetres -> metres
        total_inches = height_m / 0.0254
        feet = int(total_inches // 12)
        inches = round(total_inches - feet * 12)
        if inches == 12:
            feet, inches = feet + 1, 0
        weight_kg = raw["weight"] / 10.0           # hectograms -> kilograms

        abilities = [a["ability"]["name"].replace("-", " ").title()
                     for a in raw["abilities"] if not a["is_hidden"]]
        hidden = [a["ability"]["name"].replace("-", " ").title()
                  for a in raw["abilities"] if a["is_hidden"]]

        enriched.append({
            "dex": dex,
            "dex_str": f"{dex:04d}",
            "name": src["name"],
            "hp": stats["hp"],
            "attack": stats["attack"],
            "defense": stats["defense"],
            "sp_attack": stats["special-attack"],
            "sp_defense": stats["special-defense"],
            "speed": stats["speed"],
            "bst": api_bst,
            "types": [t["type"]["name"].title() for t in raw["types"]],
            "abilities": abilities,
            "hidden_ability": hidden[0] if hidden else None,
            "height_m": height_m,
            "height_ft": f"{feet}'{inches:02d}\"",
            "weight_kg": weight_kg,
            "weight_lbs": round(weight_kg * 2.20462, 1),
            "generation": generation(dex),
            "sprite": raw["sprites"]["front_default"],
        })

    enriched.sort(key=lambda p: p["dex"])
    OUT.write_text(json.dumps(enriched, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {len(enriched)} entries to {OUT}")
    if mismatches:
        print(f"Note: {len(mismatches)} BST totals in pokemon.json disagree with "
              "current PokeAPI stats (old-generation stats / data errors); "
              "API values were used:")
        for m in mismatches:
            print("  ", m)
    else:
        print("BST cross-check: all match pokemon.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
