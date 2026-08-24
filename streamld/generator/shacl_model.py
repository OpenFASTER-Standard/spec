"""Layer 1: SHACL extractor. Mirrors engine/xsd_model.py's role for mikadiv-vib/:
parses a SHACL shapes file and answers "what fields does shape X have, with
what type/cardinality?" No hand-typed content — everything is read from the
shapes graph.
"""
from __future__ import annotations

from dataclasses import dataclass

from rdflib import Graph
from rdflib.namespace import SH


@dataclass(frozen=True)
class Field:
    name: str
    datatype: str | None
    min_count: int
    max_count: int | None


def load_shapes(path: str) -> Graph:
    graph = Graph()
    graph.parse(path, format="turtle")
    return graph


def fields_for_shape(graph: Graph, shape_iri) -> list[Field]:
    fields = []
    for prop_bnode in graph.objects(shape_iri, SH.property):
        path = graph.value(prop_bnode, SH.path)
        datatype = graph.value(prop_bnode, SH.datatype)
        min_count = graph.value(prop_bnode, SH.minCount)
        max_count = graph.value(prop_bnode, SH.maxCount)

        fields.append(
            Field(
                name=str(path).rsplit("#", maxsplit=1)[-1],
                datatype=str(datatype).rsplit("#", maxsplit=1)[-1] if datatype else None,
                min_count=int(min_count) if min_count is not None else 0,
                max_count=int(max_count) if max_count is not None else None,
            )
        )
    return sorted(fields, key=lambda f: f.name)
