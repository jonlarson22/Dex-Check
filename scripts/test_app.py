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

# sprite regression guard: any sprite column present must use the raw
# 'sprite' key or the ImageColumn config stops matching (URLs as text)
for f in frames(at):
    for c in f.columns:
        if c.lower() == "sprite":
            assert c == "sprite", f"sprite column renamed to {c!r}"
print("2. sprite column key intact (ImageColumn will match)")

# combined table: searched Pokemon is the highlighted top row, no Set
# column, and the redundant 'You searched' header line is gone
electrode = [f for f in frames(at)
             if "Name" in f.columns and "Electrode" in f["Name"].tolist()]
frame = electrode[0]
row = frame.iloc[0]
assert row["Name"] == "Electrode", row
assert "Set" not in frame.columns, list(frame.columns)
assert not any("You searched" in (m.value or "") for m in at.markdown), \
    "redundant 'You searched' header still present"
for c in ["HP", "Atk", "Def", "SpA", "SpD", "Spe", "BST", "Abilities",
          "Height", "Weight (lbs)", "Gen"]:
    assert c in frame.columns, f"combined row missing column {c}"
assert int(row["BST"]) == 490 and int(row["Spe"]) == 150, row
# Metapod has no hidden ability: must not render 'nan'
metapod = frame[frame["Name"] == "Metapod"].iloc[0]
assert metapod["Abilities"] == "Shed Skin", metapod["Abilities"]
print("3. combined table, highlighted top row, no Set/header OK")

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

# ---- 9. his Pineco screenshot: Cherubi must show 'Chlorophyll', not 'nan'
at = fresh()
at.selectbox(key="quick1").set_value("0204 Pineco")
at.run(timeout=120)
assert not at.exception, at.exception
for f in frames(at):
    if "Abilities" in f.columns:
        for val in f["Abilities"].astype(str):
            assert "nan" not in val, f"'nan' leaked into abilities: {val}"
pineco = [f for f in frames(at)
          if "Name" in f.columns and "Pineco" in f["Name"].tolist()][0]
cherubi = pineco[pineco["Name"] == "Cherubi"].iloc[0]
assert cherubi["Abilities"] == "Chlorophyll", cherubi["Abilities"]
assert pineco.iloc[0]["Name"] == "Pineco"
assert len(pineco) == 6  # Pineco + Arbok, Golbat, Magby, Kricketot, Cherubi
print("9. no-'nan' hidden ability fix OK")

print("ALL TESTS PASSED")
