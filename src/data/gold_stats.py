from collections import Counter, defaultdict

from .annotate_io import GOLD_ANN, GOLD_DOCS
from src.json_io import read_jsonl
from src.schema import Annotation, Doc

docs = {d.id: d for d in read_jsonl(GOLD_DOCS, Doc)}
cells: dict[str, Counter] = defaultdict(Counter)
for a in read_jsonl(GOLD_ANN, Annotation):
    c = cells[f"{docs[a.doc_id].lang}/{docs[a.doc_id].genre}"]
    c["items"] += 1
    c["excluded"] += int(a.excluded)
    if not a.excluded:
        c["spans"] += len(a.spans)
        c["no_place"] += int(len(a.spans) == 0)
        for s in a.spans:
            for f in s.flags:
                c[f"flag_{f}"] += 1

cols = ["items", "excluded", "spans", "no_place", "flag_fig", "flag_unsure", "flag_hist"]
print("cell".ljust(14) + "".join(c.rjust(13) for c in cols))
for name, c in sorted(cells.items()):
    print(name.ljust(14) + "".join(str(c[k]).rjust(13) for k in cols))
# python -m src.data.gold_stats