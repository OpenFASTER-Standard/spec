import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from generator.shacl_model import load_shapes, fields_for_shape
from rdflib.namespace import Namespace

SHAPES_PATH = Path(__file__).parent.parent / "model" / "envelope.ttl"
STREAMLD = Namespace("https://openfaster.org/streamld#")

SHAPE_CLASS_PAIRS = [
    (STREAMLD.EventEnvelopeShape, STREAMLD.EventEnvelope),
    (STREAMLD.ReplicationFrameShape, STREAMLD.ReplicationFrame),
    (STREAMLD.SubscriptionRequestShape, STREAMLD.SubscriptionRequest),
    (STREAMLD.GapSignalShape, STREAMLD.GapSignal),
]


def test_shacl2code_mirror_matches_pyshacl_shapes():
    graph = load_shapes(SHAPES_PATH)

    for shape_iri, class_iri in SHAPE_CLASS_PAIRS:
        shape_fields = fields_for_shape(graph, shape_iri)
        mirror_fields = fields_for_shape(graph, class_iri)

        assert shape_fields == mirror_fields, (
            f"{shape_iri} (validated by pyshacl) and its shacl2code mirror "
            f"{class_iri} have drifted — keep their sh:property lists in "
            f"sync in envelope.ttl."
        )
