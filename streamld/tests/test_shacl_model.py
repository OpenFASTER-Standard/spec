import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from rdflib import Namespace

from generator.shacl_model import Field, fields_for_shape, load_shapes

STREAMLD = Namespace("https://openfaster.org/streamld#")
SHAPES_PATH = str(Path(__file__).parent.parent / "model" / "envelope.ttl")


def test_fields_for_event_envelope_shape():
    graph = load_shapes(SHAPES_PATH)

    fields = fields_for_shape(graph, STREAMLD.EventEnvelopeShape)

    names = [f.name for f in fields]
    assert names == sorted(names)
    assert Field(name="isSnapshot", datatype="boolean", min_count=1, max_count=1) in fields
    assert Field(name="sequence", datatype="integer", min_count=1, max_count=1) in fields
    assert Field(name="streamId", datatype="string", min_count=1, max_count=1) in fields
    assert Field(name="payload", datatype=None, min_count=1, max_count=1) in fields


def test_fields_for_subscription_request_shape_has_optional_after():
    graph = load_shapes(SHAPES_PATH)

    fields = fields_for_shape(graph, STREAMLD.SubscriptionRequestShape)

    after_field = next(f for f in fields if f.name == "after")
    assert after_field.min_count == 0
    assert after_field.max_count == 1
