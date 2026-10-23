from collections import Counter

from datasets import load_dataset

# wikinews dataset specs
ds = load_dataset("Fumika/Wikinews-multilingual", split="train", streaming=True)
print(next(iter(ds)).keys())
for i, row in enumerate(ds):
    print({k: (str(v)[:80]) for k, v in row.items()})
    if i == 2: break

print(Counter(ds["type"]).most_common())
print(Counter(ds["lang"]).most_common(12))
row = next(r for r in ds if r["lang"] == "de")
print(row["type"], str(row["text"])[:600])

# wikimedia dataset specs
ds_wiki = load_dataset(
    "wikimedia/wikipedia",
    "20231101.en",
    split="train",
    streaming=True,
)

ds_wiki = ds_wiki.shuffle(seed=42, buffer_size=10_000).take(5)
print(next(iter(ds)).keys())

for i, row in enumerate(ds_wiki):
    print({k: str(v)[:80] for k, v in row.items()})