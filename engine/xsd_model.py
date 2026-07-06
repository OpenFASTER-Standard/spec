"""Layer 1: machine-readable model of the MiKaDiv XSD.

Loads ``ThirdPartyDisclosureRequest.xsd`` with :mod:`xmlschema` and exposes the
field-level facts the template generator needs - descriptions, human-readable
type/format strings, requiredness, cardinality and enumerations (values *and*
their meanings) - all sourced directly from the schema. Nothing here is
hand-typed content: every string returned comes from the XSD's own
``xs:documentation`` and facets, so the Excel template, the documentation and
the specification can never drift from the schema.

The template's *shape* (which sheets exist, how nested choices collapse into
columns, the presentation-only helper columns) lives in the mapping layer
(each module's ``mapping.py``); this module only answers "what does the schema say
about field X of type Y?".
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterator, Optional

import xmlschema
from xmlschema.validators import XsdComplexType, XsdElement, XsdGroup

XS = "{http://www.w3.org/2001/XMLSchema}"
XML_LANG = "{http://www.w3.org/XML/1998/namespace}lang"

# Friendly type/format labels for named simple types whose meaning is richer
# than their raw facets convey (patterns, ISO references, ...). These are format
# descriptions, not field content, and mirror the standards the XSD cites.
FRIENDLY_TYPES: dict[str, str] = {
    "UUIDType": "UUID (xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx)",
    "CountryISO3166Alpha2Type": "Country code (ISO 3166-1 alpha-2, 2 uppercase letters)",
    "ISINISO6166Type": "ISIN (ISO 6166, 12 chars: 2 letters + 10 alphanumeric)",
    "SwiftBICCodeType": "BIC (ISO 9362, 8 or 11 alphanumeric)",
    "LEIISO17442Type": "LEI (ISO 17442, 20 alphanumeric)",
    "GermanTaxIdType": "Numeric string (German IdNr, exactly 11 digits)",
    "GermanBusinessIdType": "Numeric string (German Wirtschafts-IdNr, 13 digits)",
    "GermanTaxNumberType": "Numeric string (German Steuernummer, 13 digits)",
    "BZSTTaxNumberType": "Numeric string (German Steuernummer, 13 digits)",
    "DateOfBirthType": "Date (YYYY-MM-DD; partial 0000 allowed)",
    "COAFType": "Text (Corporate Action Event Reference, max 16)",
    "Number5Type": "Integer (0 - 99999)",
}


@dataclass(frozen=True)
class Field:
    """A resolved leaf field (element or attribute) as described by the XSD."""

    name: str
    description: str
    type_display: str
    required: bool
    max_occurs: Optional[int]  # None == unbounded


class XsdModel:
    def __init__(self, path: str):
        self.schema = xmlschema.XMLSchema(path)

    # ------------------------------------------------------------------ #
    # Documentation helpers
    # ------------------------------------------------------------------ #
    @staticmethod
    def _docs_en(documentation) -> str:
        """English text from a list of xs:documentation elements (else first)."""
        for doc in documentation:
            if doc.get(XML_LANG) == "en":
                return (doc.text or "").strip()
        for doc in documentation:
            return (doc.text or "").strip()
        return ""

    @classmethod
    def _annotation_doc(cls, component) -> str:
        """English documentation of a schema component (element/attribute/type)."""
        annotation = getattr(component, "annotation", None)
        if annotation is None:
            return ""
        return cls._docs_en(annotation.documentation)

    def _description(self, component) -> str:
        """Field description: prefer the element/attribute's own doc, else its
        type's doc (so terse elements like ``ISIN`` inherit the ISIN type doc)."""
        own = self._annotation_doc(component)
        if own:
            return own
        xsd_type = getattr(component, "type", None)
        if xsd_type is not None:
            return self._annotation_doc(xsd_type)
        return ""

    # ------------------------------------------------------------------ #
    # Type / format helpers
    # ------------------------------------------------------------------ #
    @staticmethod
    def _facet_value(xsd_type, qname: str):
        node = xsd_type
        while node is not None:
            facets = getattr(node, "facets", None)
            if facets and qname in facets:
                return getattr(facets[qname], "value", None)
            node = getattr(node, "base_type", None)
        return None

    def _type_display(self, xsd_type) -> str:
        local = getattr(xsd_type, "local_name", None)
        if local in FRIENDLY_TYPES:
            return FRIENDLY_TYPES[local]

        root = getattr(xsd_type, "root_type", None)
        kind = getattr(root, "local_name", None)

        if kind == "string":
            max_len = getattr(xsd_type, "max_length", None)
            return f"Text (max {max_len})" if max_len else "Text"
        if kind == "boolean":
            return "Boolean (true / false)"
        if kind == "date":
            return "Date (YYYY-MM-DD)"
        if kind == "dateTime":
            return "DateTime (YYYY-MM-DDThh:mm:ss)"
        if kind == "decimal":
            fraction = self._facet_value(xsd_type, f"{XS}fractionDigits")
            total = self._facet_value(xsd_type, f"{XS}totalDigits")
            if fraction:  # decimals with a fractional part
                return f"Decimal ({total} digits total, {fraction} decimals)"
            return "Integer"
        return "Text"

    # ------------------------------------------------------------------ #
    # Component lookup
    # ------------------------------------------------------------------ #
    def _type(self, type_name: str) -> XsdComplexType:
        return self.schema.types[type_name]

    def _iter_elements(self, xsd_type) -> Iterator[XsdElement]:
        """Yield every element declared by a complex type, descending into
        nested (named or anonymous) complex types so choices/sequences flatten."""
        content = getattr(xsd_type, "content", None)
        if content is None:
            return
        for element in content.iter_elements():
            yield element
            child = element.type
            if child is not None and child.is_complex() and child.content is not None:
                yield from self._iter_elements(child)

    def _iter_attributes(self, xsd_type):
        """Yield every attribute of a complex type and of its nested complex
        types (e.g. the DepositaryReceipt block's attribute)."""
        for attribute in getattr(xsd_type, "attributes", {}).values():
            yield attribute
        for element in self._iter_elements(xsd_type):
            child = element.type
            if child is not None and child.is_complex():
                for attribute in getattr(child, "attributes", {}).values():
                    yield attribute

    def _field_from(self, component, *, is_attribute: bool,
                    description: Optional[str], required: Optional[bool]) -> Field:
        desc = description if description is not None else self._description(component)
        if required is None:
            required = (component.use == "required") if is_attribute else (component.min_occurs or 0) >= 1
        max_occurs = None if is_attribute else component.max_occurs
        return Field(
            name=component.local_name,
            description=desc,
            type_display=self._type_display(component.type),
            required=required,
            max_occurs=max_occurs,
        )

    # ------------------------------------------------------------------ #
    # Public API
    # ------------------------------------------------------------------ #
    def elem(self, type_name: str, field_name: str, *,
             description: Optional[str] = None, required: Optional[bool] = None) -> Field:
        """First element named ``field_name`` reachable from ``type_name``."""
        for element in self._iter_elements(self._type(type_name)):
            if element.local_name == field_name:
                return self._field_from(element, is_attribute=False,
                                        description=description, required=required)
        raise KeyError(f"element {field_name!r} not found in type {type_name!r}")

    def attr(self, type_name: str, field_name: str, *,
             description: Optional[str] = None, required: Optional[bool] = None) -> Field:
        """First attribute named ``field_name`` on ``type_name`` (or a nested type)."""
        for attribute in self._iter_attributes(self._type(type_name)):
            if attribute.local_name == field_name:
                return self._field_from(attribute, is_attribute=True,
                                        description=description, required=required)
        raise KeyError(f"attribute {field_name!r} not found in type {type_name!r}")

    def path(self, type_name: str, names: list[str], *,
             description: Optional[str] = None, required: Optional[bool] = None) -> Field:
        """Resolve a nested element by walking a path of element names, e.g.
        ``["Receipts", "MoreThan1000Available"]`` - disambiguates fields that
        share a name across different branches."""
        current = self._type(type_name)
        component = None
        for depth, name in enumerate(names):
            component = next(
                (e for e in self._iter_elements(current) if e.local_name == name),
                None,
            )
            if component is None:
                raise KeyError(f"path {names!r} broke at {name!r} in {type_name!r}")
            if depth < len(names) - 1:
                current = component.type
        return self._field_from(component, is_attribute=False,
                                description=description, required=required)

    def enum(self, type_name: str) -> tuple[list[str], dict[str, str]]:
        """Values and English meanings of a named enumeration simple type."""
        return self._enum_from_elem(self._type(type_name).elem)

    def inline_enum(self, type_name: str, field_name: str) -> tuple[list[str], dict[str, str]]:
        """Values and meanings of an anonymous enumeration on an element."""
        for element in self._iter_elements(self._type(type_name)):
            if element.local_name == field_name:
                return self._enum_from_elem(element.elem)
        raise KeyError(f"element {field_name!r} not found in type {type_name!r}")

    def _enum_from_elem(self, elem) -> tuple[list[str], dict[str, str]]:
        values: list[str] = []
        meanings: dict[str, str] = {}
        for enumeration in elem.iter(f"{XS}enumeration"):
            value = enumeration.get("value")
            values.append(value)
            annotation = enumeration.find(f"{XS}annotation")
            docs = annotation.findall(f"{XS}documentation") if annotation is not None else []
            meanings[value] = self._docs_en(docs)
        return values, meanings
