"""Web app: HTML pages and JSON API."""

import warnings

import pytest

warnings.filterwarnings("ignore")

from fastapi.testclient import TestClient  # noqa: E402

import app as appmod  # noqa: E402

client = TestClient(appmod.app)

PARAMS = {"dob": "1990-08-15", "tob": "10:30", "city": "New Delhi, India",
          "name": "Ref"}


def test_index_page():
    r = client.get("/")
    assert r.status_code == 200
    assert "Generate advice" in r.text


def test_html_report_sections():
    r = client.post("/report", data=PARAMS)
    assert r.status_code == 200
    for section in ("Education Guidance", "Career Guidance",
                    "Current Vimshottari", "Transit (Gochar) Triggers",
                    "Remedial suggestions", "Frequently Asked",
                    "Planetary Positions"):
        assert section in r.text


def test_api_report_structure():
    r = client.get("/api/report", params=PARAMS)
    assert r.status_code == 200
    d = r.json()
    for key in ("birth", "lagna", "current_dasha", "education", "career",
                "transits", "faqs"):
        assert key in d
    assert d["current_dasha"]["mahadasha"]
    assert len(d["faqs"]) == 11
    assert d["education"]["streams"]
    assert d["career"]["fields"]
    assert d["transits"]["positions"]["Saturn"]["sign"] == "Pisces"


def test_api_single_faq():
    r = client.get("/api/faq/when_job", params=PARAMS)
    assert r.status_code == 200
    d = r.json()
    assert d["question"] and d["verdict"]
    for w in d["timeline"]:
        assert w["start"] < w["end"]


def test_api_metadata_endpoints():
    assert client.get("/api/cities").status_code == 200
    faqs = client.get("/api/faqs")
    assert faqs.status_code == 200
    assert len(faqs.json()) == 11


def test_api_coordinate_path():
    r = client.get("/api/report", params={"dob": "1985-03-20", "tob": "06:15",
                                          "latitude": "19.0760",
                                          "longitude": "72.8777", "tz": "5.5"})
    assert r.status_code == 200


@pytest.mark.parametrize("params,code", [
    ({"dob": "1990-08-15", "tob": "10:30"}, 422),                 # no location
    ({"dob": "15/08/1990", "tob": "10:30", "city": "Mumbai, India"}, 422),  # bad date
])
def test_api_validation_errors(params, code):
    assert client.get("/api/report", params=params).status_code == code


def test_api_unknown_faq():
    r = client.get("/api/faq/does_not_exist", params=PARAMS)
    assert r.status_code == 404
