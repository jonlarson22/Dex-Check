"""AppTest for the Streamlit Dex Scrambler (v2).

Covers: dex-number quick search (Jonathan's original screenshot values),
name search (exact, partial-unique, ambiguous), full detail rows for the
searched Pokemon, the all-columns picker, and explorer dex search.
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


# ---- 1. dex-number quick search: his screenshot values still reproduce
at = fresh()
for key, val in (("quick1", "101"), ("quick2", "282"), ("quick3", "842")):
    at.text_input(key=key).set_value(val)
at.run(timeout=120)
assert not at.exception, at.exception
names = all_names(at)
for n in ["Metapod", "Weezing", "Wo-Chien", "Iron Leaves",
          "Houndour", "Corvisquire",
          "Tyranitar", "Masquerain", "Lopunny", "Azelf", "Blipbug"]:
    assert n in names, f"missing {n}"
print("1. dex quick search OK")

# searched Pokemon now gets a full-detail row (abilities/height/weight/gen)
electrode = [f for f in frames(at)
             if "Name" in f.columns and "Electrode" in f["Name"].tolist()]
assert electrode, "no Electrode source row"
row = electrode[0].iloc[0]
for c in ["HP", "Atk", "Def", "SpA", "SpD", "Spe", "BST", "Abilities",
          "Height", "Weight (lbs)", "Gen"]:
    assert c in electrode[0].columns, f"source row missing column {c}"
assert int(row["BST"]) == 490 and int(row["Spe"]) == 150, row
print("2. full-detail source row OK:", row["Name"], "BST", row["BST"],
      "| abilities:", row["Abilities"])

# ---- 3. name search, exact: Unfezant (his live-app screenshot, 521)
at = fresh()
at.text_input(key="quick1").set_value("unfezant")
at.run(timeout=120)
assert not at.exception, at.exception
names = all_names(at)
for n in ["Unfezant", "Electabuzz", "Chikorita", "Sneasel", "Celebi",
          "Simisage", "Pecharunt"]:
    assert n in names, f"missing {n}"
print("3. name search 'unfezant' OK")

# ---- 4. partial unique name: 'pika' -> Pikachu
at = fresh()
at.text_input(key="quick2").set_value("pika")
at.run(timeout=120)
assert not at.exception, at.exception
names = all_names(at)
for n in ["Pikachu", "Meowth", "Omanyte", "Ho-Oh", "Dewott", "Watchog"]:
    assert n in names, f"missing {n}"
print("4. partial name search 'pika' OK")

# ---- 5. ambiguous name: 'nidoran' -> disambiguation selectbox
at = fresh()
at.text_input(key="quick1").set_value("nidoran")
at.run(timeout=120)
assert not at.exception, at.exception
assert len(at.selectbox) >= 1, "no disambiguation selectbox"
opts = list(at.selectbox[0].options)
assert len(opts) == 2, opts
names = all_names(at)
assert "Nidoran♀" in names  # default pick resolves and renders
print("5. ambiguous name OK:", opts)

# ---- 6. gibberish -> warning, no crash
at = fresh()
at.text_input(key="quick1").set_value("zzzz")
at.run(timeout=120)
assert not at.exception, at.exception
assert len(at.warning) >= 1
print("6. no-match warning OK")

# ---- 7. explorer: all-columns picker can reduce to just Name + BST
at = fresh()
cols_widget = [w for w in at.multiselect if w.label == "Columns"][0]
cols_widget.set_value(["name", "bst"])
at.run(timeout=120)
assert not at.exception, at.exception
big = frames(at)[-1]
assert list(big.columns) == ["Name", "BST"], list(big.columns)
assert len(big) == 1025
print("7. column picker OK")

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
