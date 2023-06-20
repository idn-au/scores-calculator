import sys
from pathlib import Path

from rdflib import Graph, BNode, URIRef

from calculators.care import *
from calculators.parser import (
    _forward_chain_labels,
    _forward_chain_dcat,
    _forward_chain_descriptions,
)

calc_module_path = Path(Path(__file__).parent.parent / "calculators").absolute()
sys.path.insert(0, str(calc_module_path))
import pytest
from calculators import care, SCORES

CALC_MODULE_PATH = Path(__file__).parent.parent / "calculators"
sys.path.append(str(CALC_MODULE_PATH))
CARE_CALCULATOR = CALC_MODULE_PATH / "care.py"
TEST_DATA_DIR = Path(__file__).parent / "data"


@pytest.fixture
def test_g():
    # construct your graph here
    g = Graph().parse(str(TEST_DATA_DIR / "care_test_data.ttl"), format="turtle")
    _forward_chain_labels(g)
    _forward_chain_dcat(g)
    _forward_chain_descriptions(g)
    return g


@pytest.fixture
def resource():
    return URIRef(
        "https://raw.githubusercontent.com/idn-au/catalogue-data/main/data/catalogues/democat/AAC-SA.ttl"
    )


def test_calculate_c1_discoverable(resource):
    result = calculate_c1_discoverable(resource)
    assert result == 1


def test_calculate_c1_searchable(test_g):
    result = calculate_c1_searchable(test_g)
    assert result == 1


def test_calculate_c1_accessible(test_g, resource):
    result = calculate_c1_accessible(test_g, resource)
    assert result == 1


def test_calculate_a11_notices(test_g, resource):
    result = calculate_a11_notices(test_g, resource)
    assert result == 1


def test_calculate_care_c2(test_g, resource):
    result = calculate_care_c2(test_g, resource, c1_score=3)
    assert result == 3


@pytest.mark.xfail  # need to decide on business rules for last point. Other 2/3 points implemented.
# "Equitable Outcomes from data are discoverable,? If the catalogue is about the data, I am not sure how provenance can
# be measured."
def test_calculate_care_c3(test_g, resource):
    result = calculate_care_c3(test_g, resource, c2_score=3)
    assert result == 3


def test_calculate_a11_notices_2(test_g, resource):
    result = calculate_a12_licence_rights(test_g, resource)
    assert result == 2


def test_calculate_care_a21(test_g, resource):
    result = calculate_care_a2(test_g, resource, a1_score=1)
    assert result == 3


def test_calculate_a32_score(test_g, resource):
    result = calculate_a32_score(test_g, resource)
    assert result


def test_calculate_care_a3(test_g, resource):
    result = calculate_care_a3(test_g, resource, a2_score=2)
    assert result == 3


def test_calculate_r1(test_g, resource):
    result = calculate_r1(test_g, resource)
    assert result == 3


@pytest.mark.skip(reason="not implemented")
def test_calculate_r2(test_g, resource):
    result = calculate_r2(test_g, resource)
    assert result


def test_calculate_r3(test_g, resource):
    result = calculate_r3(test_g, resource)
    assert result == 6


def test_calculate_e1(test_g, resource):
    result = calculate_e1(test_g, resource)
    assert result == 3


def test_calculate_e2(test_g, resource):
    result = calculate_e2(test_g, resource)
    assert result == 3


def test_calculate_e3(test_g, resource):
    result = calculate_e3(test_g, resource)
    assert result == 3


def test_calculate_care(test_g, resource):
    calculate_care(test_g, resource)
