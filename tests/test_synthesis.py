"""Education x Career synthesis (collective recommendation)."""

from astro_adviser import synthesis as S


class _F:
    def __init__(self, title):
        self.title = title


def test_classify():
    assert S.classify("Fine arts & design") == "ARTS"
    assert S.classify("Medicine (physician)") == "MEDICINE"
    assert S.classify("Information technology & software") == "IT"
    assert S.classify("Law & judiciary") == "LAW"


def test_arts_plus_medicine_gives_plastic_surgeon():
    out = S.synthesize([_F("Fine arts & design")], [_F("Medicine (physician)")])
    titles = [o["title"] for o in out]
    assert "Plastic & cosmetic surgeon" in titles
    # carries the linkage fields
    assert out[0]["education_field"] == "Fine arts & design"
    assert out[0]["career_field"] == "Medicine (physician)"


def test_other_known_combos():
    maths_it = [o["title"] for o in
                S.synthesize([_F("Mathematics & statistics")],
                             [_F("Information technology & software")])]
    assert any("scientist" in t.lower() or "ai" in t.lower() for t in maths_it)
    comm_law = [o["title"] for o in
                S.synthesize([_F("Commerce & accountancy")], [_F("Law & judiciary")])]
    assert any("lawyer" in t.lower() or "tax" in t.lower() for t in comm_law)


def test_fallback_is_readable():
    out = S.synthesize([_F("Liberal arts")], [_F("Power / energy sector")])
    assert out and out[0]["title"]          # never empty when both present


def test_empty_inputs():
    assert S.synthesize([], [_F("Medicine")]) == []
    assert S.synthesize([_F("Arts")], []) == []


def test_report_career_has_linked_fields(report):
    assert isinstance(report.career.linked_fields, list)
    assert report.career.linked_fields          # at least one collective result
    for l in report.career.linked_fields:
        assert l["title"] and l["education_field"] and l["career_field"]
