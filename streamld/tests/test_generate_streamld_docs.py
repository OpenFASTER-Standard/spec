import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from generator.generate_streamld_docs import render_bikeshed_include

SHAPES_PATH = str(Path(__file__).parent.parent / "model" / "envelope.ttl")


def test_render_bikeshed_include_contains_all_shapes():
    output = render_bikeshed_include(SHAPES_PATH)

    assert '<h3 id="eventenvelope-fields">EventEnvelope</h3>' in output
    assert "<code>sequence</code>" in output
    assert "<code>isSnapshot</code>" in output
    assert '<h3 id="replicationframe-fields">ReplicationFrame</h3>' in output
    assert '<h3 id="subscriptionrequest-fields">SubscriptionRequest</h3>' in output
    assert '<h3 id="gapsignal-fields">GapSignal</h3>' in output

    # No raw Markdown pipe-table syntax should leak through.
    assert "| --- |" not in output
    assert "| Field | Type | Required |" not in output


def test_render_bikeshed_include_marks_required_fields():
    output = render_bikeshed_include(SHAPES_PATH)

    lines = output.splitlines()
    sequence_line = next(line for line in lines if "<code>sequence</code>" in line)
    after_line = next(line for line in lines if "<code>after</code>" in line)

    assert sequence_line.rstrip().endswith("<td>Yes</tr>")
    assert after_line.rstrip().endswith("<td>No</tr>")
