# Pokémon National Dex Scrambler

Enter a dex number and see every other Pokémon whose dex number uses the
same digits — e.g. 0101 Electrode scrambles to 0011 Metapod, 0110 Weezing,
1001 Wo-Chien and 1010 Iron Leaves — with full stats, types, abilities,
height and weight.

## Streamlit app (current version)

- **Main file:** `app.py` (repo root)
- **Data:** `data/pokemon_full.json` — all 1,025 Pokémon, regenerated from
  [PokéAPI](https://pokeapi.co) with `python3 scripts/fetch_data.py`
- **Hosting:** Streamlit Cloud — repo `jonlarson22/Dex-Check`, branch
  `main`, main file path `app.py`

Features: quick search for up to three Pokémon at once via a
type-to-filter dropdown (search by name or dex number). Each result is a
single table — the searched Pokémon highlighted on the top row, its
scrambles below — showing sprite, types, all six stats, abilities,
height, weight and generation, so everything scrolls together. Plus a
full Dex explorer with name/dex search, type/generation filters, a BST
range slider, sortable columns, and a column picker (Sprite, Dex and
Name are always shown). Every column has a data-computed width, and the
numeric columns (Dex, stats, heights, weights, Gen) are centered.

### Data note

The original `pokemon.json` BST totals turned out to mix generations
(pre-buff stats for some older Pokémon) and contain errors in many
Gen 9 entries (e.g. Pawmi was listed as 290; it's 240). The Streamlit app
uses current-generation base stats summed from PokéAPI. Form notes:
Minior = Meteor form, Terapagos = Normal form, Zacian/Zamazenta = Hero
form (the PokéAPI defaults). The old file is kept for the legacy page.

## Legacy static page

`index.html` + `pokemon.json` — the original GitHub Pages version
(name + BST only). Kept as-is; the Streamlit app supersedes it.
