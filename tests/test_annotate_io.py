import pytest

from src.data.annotate_io import parse_marked


def test_parse_marked_offsets():
    plain, spans = parse_marked("Er kam aus [[Tupelo]], [[Mississippi|unsure]].")
    assert plain == "Er kam aus Tupelo, Mississippi."
    assert [(s.start, s.end, s.surface) for s in spans] == [(11, 17, "Tupelo"), (19, 30, "Mississippi")]
    assert spans[1].flags == ["unsure"]

def test_unbalanced_markup_fails():
    with pytest.raises(ValueError):
        parse_marked("Er kam aus [[Tupelo.")

def test_unknown_flag_fails():
    with pytest.raises(ValueError):
        parse_marked("[[Berlin|foo]]")