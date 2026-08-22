import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from generator.generate_streamld_docs import render_bikeshed_include

SHAPES_PATH = str(Path(__file__).parent.parent / "model" / "envelope.ttl")


def test_render_bikeshed_include_contains_all_shapes():
    output = render_bikeshed_include(SHAPES_PATH)

    assert "## EventEnvelope ##" in output
    assert "`sequence`" in output
    assert "`isSnapshot`" in output
    assert "## ReplicationFrame ##" in output
    assert "## SubscriptionRequest ##" in output
    assert "## GapSignal ##" in output


def test_render_bikeshed_include_marks_required_fields():
    output = render_bikeshed_include(SHAPES_PATH)

    lines = output.splitlines()
    sequence_line = next(line for line in lines if "`sequence`" in line)
    after_line = next(line for line in lines if "`after`" in line)

    assert "| Yes |" in sequence_line
    assert "| No |" in after_line
