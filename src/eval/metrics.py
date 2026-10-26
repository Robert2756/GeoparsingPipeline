import random
from dataclasses import dataclass

from src.schema import Annotation, Doc, Span


@dataclass(frozen=True)
class Counts:
    tp: int = 0
    fp: int = 0
    fn: int = 0

    def __add__(self, o: "Counts") -> "Counts":
        return Counts(self.tp + o.tp, self.fp + o.fp, self.fn + o.fn)

    # of everything the system predicted, what fraction was correct?
    @property
    def precision(self) -> float:
        return self.tp / (self.tp + self.fp) if self.tp + self.fp else 0.0

    # of all the correct gold mentions, what fraction did the system find?
    @property
    def recall(self) -> float:
        return self.tp / (self.tp + self.fn) if self.tp + self.fn else 0.0

    # F1 combines precision and recall into one score
    @property
    def f1(self) -> float:
        if self.tp + self.fp + self.fn == 0:  # nothing to find, nothing predicted
            return 1.0
        p, r = self.precision, self.recall
        return 2 * p * r / (p + r) if p + r else 0.0


# checks whether two character spans intersect
def _overlap(a: Span, b: Span) -> bool:
    return a.start < b.end and b.start < a.end


# called for each doc
def match_doc(gold: list[Span], pred: list[Span], mode: str = "strict",
              ignore_flags: frozenset[str] = frozenset()) -> Counts:
    ignorable = [g for g in gold if set(g.flags) & ignore_flags]
    gold = [g for g in gold if not set(g.flags) & ignore_flags] # get golds
    mg: set[int] = set() # indices of matched gold spans
    mp: set[int] = set() # indices of matched predictions
    # multiple matching rules
    passes = [lambda g, p: (g.start, g.end) == (p.start, p.end)] # pass function to list -> exact start and end positions RULE 1
    if mode == "lenient":
        passes.append(_overlap) # pass second function to list -> overlap between spans RULE 2
    for same in passes:  # loops over each rule
        for i, g in enumerate(gold): # loop over gold spans
            if i in mg: # if gold already matched continue
                continue
            for j, p in enumerate(pred): # iterate over all predictions
                if j not in mp and same(g, p): # if gold and prediction match, note indices
                    mg.add(i)
                    mp.add(j)
                    break
    # calculate false positives
    fp = sum(1 for j, p in enumerate(pred)
             if j not in mp and not any(_overlap(p, ig) for ig in ignorable))
    return Counts(len(mg), fp, len(gold) - len(mg))


def evaluate(docs: list[Doc], gold: list[Annotation], pred: list[Annotation],
             mode: str = "strict") -> list[dict]:
    g_by = {a.doc_id: a for a in gold if not a.excluded}
    p_by = {a.doc_id: a for a in pred}
    groups: dict[str, list[Counts]] = {"all": []}
    for d in docs:
        if d.id not in g_by:  # document was not annotated
            continue
        p = p_by[d.id].spans if d.id in p_by else [] # has document a prediction?
        c = match_doc(g_by[d.id].spans, p, mode)
        for key in ("all", f"{d.lang}/{d.genre}"):
            groups.setdefault(key, []).append(c)
    rows = []
    for name, cs in sorted(groups.items()): # cs is a list of Counts
        tot = sum(cs, Counts()) # added by internal Count add function
        rows.append({"group": name, "docs": len(cs), "gold_spans": tot.tp + tot.fn,
                     "precision": tot.precision, "recall": tot.recall, "f1": tot.f1})
    return rows


def format_table(rows: list[dict]) -> str:
    out = [f"{'group':<16}{'docs':>6}{'gold':>7}{'P':>7}{'R':>7}{'F1':>7}"]
    for r in rows:
        out.append(f"{r['group']:<16}{r['docs']:>6}{r['gold_spans']:>7}{r['precision']:>7.2f}"
                   f"{r['recall']:>7.2f}{r['f1']:>7.2f}")
    return "\n".join(out)