"""AppTest: render the app, then set the three quick-search boxes to the
values in Jonathan's screenshot (101, 282, 842) and check the matches
against the old page's output."""
from pathlib import Path

from streamlit.testing.v1 import AppTest

APP = Path(__file__).resolve().parent.parent / "app.py"
at = AppTest.from_file(str(APP)).run(timeout=120)
assert not at.exception, at.exception
print("initial render OK; dataframes:", len(at.dataframe))

expected = {
    "quick1": ["Metapod", "Weezing", "Wo-Chien", "Iron Leaves"],
    "quick2": ["Houndour", "Corvisquire"],
    "quick3": ["Tyranitar", "Masquerain", "Lopunny", "Azelf", "Blipbug"],
}
for key, val in (("quick1", 101), ("quick2", 282), ("quick3", 842)):
    at.number_input(key=key).set_value(val)
at.run(timeout=120)
assert not at.exception, at.exception

frames = [df.value for df in at.dataframe]
all_names = set()
for f in frames:
    if "Name" in f.columns:
        all_names.update(f["Name"].tolist())
for key, names in expected.items():
    for n in names:
        assert n in all_names, f"MISSING {n} ({key})"
    print(key, "OK ->", names)

# Full explorer table sanity: unfiltered should list all 1025
big = [f for f in frames if len(f) == 1025]
assert big, f"no 1025-row frame; sizes={[len(f) for f in frames]}"
cols = list(big[0].columns)
print("explorer columns:", cols)
for c in ["HP", "Atk", "Def", "SpA", "SpD", "Spe", "BST", "Abilities",
          "Height", "Weight (lbs)", "Gen", "Scrambles To"]:
    assert c in cols, f"missing column {c}"
row842 = big[0][big[0]["Dex"] == "0842"].iloc[0]
print("0842 row:", row842["Name"], row842["BST"], "| scrambles:", row842["Scrambles To"])
print("ALL TESTS PASSED")
