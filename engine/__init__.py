"""OpenFASTER generation engine (module-agnostic).

Shared building blocks used by every OpenFASTER module (MiKaDiv today, FASTER
later): the XSD extractor (:mod:`engine.xsd_model`) and the template/document
renderer (:mod:`engine.generator`). Module-specific content lives in each
module package (e.g. ``mikadiv``), never here.
"""
