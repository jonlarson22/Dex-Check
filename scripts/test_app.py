"""AppTest for the Streamlit Dex Scrambler (v3).

Covers: the type-to-filter dropdown quick search (by label = dex + name),
full detail rows for the searched Pokemon, the sprite column regression
(the dataframe column must stay named 'sprite' or the ImageColumn config
stops matching and URLs render as text), permanent Sprite/Dex/Name
explorer columns, and explorer dex search.
"""
from pathlib import Path

from streamlit.testing.v1 import AppTest

APP = Path(__file__).resolve().parent.parent / "app.py"


def fresh():
    at = AppTest.from_file(str(APP)).run(timeout=120)
    assert not at.exception, at.exception
    return at


def frames(at):
    return [df.value for df in at.dataframe]


def all_names(at):
    names = set()
    for f in frames(at):
        if "Name" in f.columns:
            names.update(f["Name"].tolist())
    return names


# ---- 1. dropdown quick search: his original screenshot values
at = fresh()
for key, label in (("quick1", "0101 Electrode"),
                   ("quick2", "0282 Gardevoir"),
                   ("quick3", "0842 Appletun")):
    at.selectbox(key=key).set_value(label)
at.run(timeout=120)
assert not at.exception, at.exception
names = all_names(at)
for n in ["Metapod", "Weezing", "Wo-Chien", "Iron Leaves",
          "Houndour", "Corvisquire",
          "Tyranitar", "Masquerain", "Lopunny", "Azelf", "Blipbug"]:
    assert n in names, f"missing {n}"
print("1. dropdown dex search OK")

# sprite regression guard: first column of every table is raw 'sprite'
for f in frames(at):
    assert list(f.columns)[0] == "sprite", list(f.columns)
print("2. sprite column key intact (ImageColumn will match)")

# searched Pokemon gets a full-detail row
electrode = [f for f in frames(at)
             if "Name" in f.columns and "Electrode" in f["Name"].tolist()]
row = electrode[0].iloc[0]
for c in ["HP", "Atk", "Def", "SpA", "SpD", "Spe", "BST", "Abilities",
          "Height", "Weight (lbs)", "Gen"]:
    assert c in electrode[0].columns, f"source row missing column {c}"
assert int(row["BST"]) == 490 and int(row["Spe"]) == 150, row
print("3. full-detail source row OK")

# ---- 4. dropdown options: all 1025, searchable by name or number
at = fresh()
opts = list(at.selectbox(key="quick1").options)
assert len(opts) == 1025, len(opts)
for label in ["0025 Pikachu", "0029 Nidoran♀", "0032 Nidoran♂",
              "0521 Unfezant", "1025 Pecharunt"]:
    assert label in opts, label
print("4. dropdown options OK (1025)")

# ---- 5. his 'Iron' search: picking Lairon from the filtered list
at = fresh()
at.selectbox(key="quick1").set_value("0305 Lairon")
at.run(timeout=120)
assert not at.exception, at.exception
names = all_names(at)
for n in ["Lairon", "Clefairy", "Persian", "Milotic", "Samurott",
          "Excadrill"]:
    assert n in names, f"missing {n}"
print("5. '0305 Lairon' scramble set OK")

# ---- 6. Unfezant via dropdown (his live screenshot case)
at = fresh()
at.selectbox(key="quick3").set_value("0521 Unfezant")
at.run(timeout=120)
assert not at.exception, at.exception
names = all_names(at)
for n in ["Unfezant", "Electabuzz", "Chikorita", "Sneasel", "Celebi",
          "Simisage", "Pecharunt"]:
    assert n in names, f"missing {n}"
print("6. Unfezant scramble set OK")

# ---- 7. explorer: Sprite/Dex/Name are permanent even if picker is emptied
at = fresh()
cols_widget = [w for w in at.multiselect if w.label == "Columns"][0]
assert "sprite" not in list(cols_widget.options)
assert "dex_str" not in list(cols_widget.options)
assert "name" not in list(cols_widget.options)
cols_widget.set_value(["bst"])
at.run(timeout=120)
assert not at.exception, at.exception
big = frames(at)[-1]
assert list(big.columns) == ["sprite", "Dex", "Name", "BST"], \
    list(big.columns)
assert len(big) == 1025
print("7. permanent columns OK")

# ---- 8. explorer search by dex number finds Unfezant
at = fresh()
search = [w for w in at.text_input
          if w.label == "Search by name or dex number"][0]
search.set_value("521")
at.run(timeout=120)
assert not at.exception, at.exception
big = frames(at)[-1]
assert list(big["Name"]) == ["Unfezant"], list(big["Name"])
print("8. explorer dex search OK")

print("ALL TESTS PASSED")
