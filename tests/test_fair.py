import sys
from pathlib import Path

from rdflib import Graph, BNode, URIRef

from calculators.fair import calculate_i
from calculators.functions import (
    shared_vocabs_ontologies,
    machine_readability_score,
    licensing_score,
    provenance_score,
    data_source_score,
)

calc_module_path = Path(Path(__file__).parent.parent / "calculators").absolute()
sys.path.insert(0, str(calc_module_path))
import pytest
from calculators import fair, SCORES


CALC_MODULE_PATH = Path(__file__).parent.parent / "calculators"
sys.path.append(str(CALC_MODULE_PATH))
FAIR_CALCULATOR = CALC_MODULE_PATH / "calc_fair.py"
TEST_DATA_DIR = Path(__file__).parent / "data"


def test_invalid_input():
    with pytest.raises(ValueError):
        g = fair.main(TEST_DATA_DIR / "test_input_invalid_01.ttl", "graph", True)


def test_valid_input():
    g = fair.main(TEST_DATA_DIR / "AGIL.ttl", "graph", True)
    assert isinstance(g, Graph)


def test_agil_f_score():
    g = fair.main(TEST_DATA_DIR / "AGIL.ttl", "graph", True)
    f = None
    for o in g.objects(None, SCORES.fairFScore):
        f = int(o)

    assert f == 14


def test_agil_i_score():
    g = Graph().parse(str(TEST_DATA_DIR / "AGIL.ttl"), format="turtle")
    resource = URIRef(
        "https://data.gov.au/data/dataset/34b1c164-fbe8-44a0-84fd-467dba645aa7"
    )
    testing_bnode = BNode()
    results = calculate_i(g, resource, testing_bnode)
    for o in results.objects(None, SCORES.fairIScore):
        f = int(o)
    assert f == 6


def test_machine_readability_score():
    g = Graph().parse(str(TEST_DATA_DIR / "AGIL.ttl"), format="turtle")
    resource = URIRef(
        "https://data.gov.au/data/dataset/34b1c164-fbe8-44a0-84fd-467dba645aa7"
    )
    component_score = machine_readability_score(g, resource)
    assert component_score == 1


def test_shared_vocabs_ontologies():
    g = Graph().parse(str(TEST_DATA_DIR / "AGIL.ttl"), format="turtle")
    resource = URIRef(
        "https://data.gov.au/data/dataset/34b1c164-fbe8-44a0-84fd-467dba645aa7"
    )
    component_score = shared_vocabs_ontologies(g, resource)
    assert component_score == 1


def test_licensing_score():
    g = Graph().parse(str(TEST_DATA_DIR / "AGIL.ttl"), format="turtle")
    resource = URIRef(
        "https://data.gov.au/data/dataset/34b1c164-fbe8-44a0-84fd-467dba645aa7"
    )
    component_score = licensing_score(g, resource)
    assert component_score == 2


def test_provenance_score():
    g = Graph().parse(str(TEST_DATA_DIR / "AGIL.ttl"), format="turtle")
    resource = URIRef(
        "https://data.gov.au/data/dataset/34b1c164-fbe8-44a0-84fd-467dba645aa7"
    )
    component_score = provenance_score(g)
    assert component_score == 2


def test_data_source_score():
    g = Graph().parse(str(TEST_DATA_DIR / "made_up_test_data.ttl"), format="turtle")
    resource = URIRef("https://example.com/dataset")
    component_score = data_source_score(g, resource)
    assert component_score == 1
