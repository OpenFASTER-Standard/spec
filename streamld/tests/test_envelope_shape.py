from pathlib import Path

import pytest
from pyshacl import validate
from rdflib import Graph

SHAPES_PATH = str(Path(__file__).parent.parent / "model" / "envelope.ttl")
EXAMPLES_DIR = Path(__file__).parent.parent / "examples"


def _validate(example_filename):
    data_graph = Graph()
    data_graph.parse(str(EXAMPLES_DIR / example_filename), format="json-ld")
    conforms, _, results_text = validate(
        data_graph,
        shacl_graph=SHAPES_PATH,
        data_graph_format="json-ld",
        shacl_graph_format="turtle",
    )
    return conforms, results_text


def test_valid_envelope_conforms():
    conforms, results_text = _validate("envelope-valid.jsonld")
    assert conforms, results_text


def test_invalid_envelope_is_rejected():
    conforms, _ = _validate("envelope-invalid.jsonld")
    assert not conforms
