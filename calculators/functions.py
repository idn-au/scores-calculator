from collections import Counter
from typing import List

from rdflib import Literal, DCTERMS, PROV, DCAT, RDFS, URIRef, Graph, XSD

from reference_data.reference import (
    properties_expected_to_have_objects_with_uris,
    machine_readable_formats_to_mime_types,
    properties_for_mediatypes_formats,
    data_usage_license_properties,
    additional_provenance_properties,
    searchable_properties,
)


def machine_readability_score(metadata: Graph, resource: URIRef):
    """Calculate machine readability of text.
    Checks if the format is machine readable using a list of common machine readable mime types, and their file extensions.

    If the metadata declares a mime type using either a dcterms:format or a dcat:mediaType property, a score of 2 is given,
    else if a machine readable file extension is declared using the same properties, a score of 1 is given, else a score
    of 0 is given. A maximum score of 2 is possible - if a mime type and a file extension are both declared, a score of
    2 is given for the mime type.
    """
    format_literals = [
        str(o)
        for (_, _, o) in metadata.triples_choices(
            (resource, properties_for_mediatypes_formats, None)
        )
    ]
    value = 0
    for literal in format_literals:
        if str(literal) in machine_readable_formats_to_mime_types.values():
            return 2
        elif str(literal) in machine_readable_formats_to_mime_types.keys():
            value = (
                1  # don't return in case any other literal are a recognised mime type
            )
    return value


def shared_vocabs_ontologies(metadata: Graph, resource: URIRef):
    """Check if the objects for the following properties are URIs.
    The assumption here is that if they use URIs, those URIs refer to a shared vocabularies and ontologies."""
    object_types = [
        type(o)
        for s, p, o in metadata.triples_choices(
            (resource, properties_expected_to_have_objects_with_uris, None)
        )
    ]
    n_objects = len(object_types)
    if n_objects > 0:
        type_count = Counter(object_types)
        uris_count = type_count.get(URIRef, 0)
        literals_count = type_count.get(Literal, 0)
        if uris_count == 0:
            return 0  # no URIs, so assume no shared vocabularies
        elif literals_count == 0:
            return 2  # no literals, so all URIs are assumed from shared vocabularies
        else:
            if uris_count > literals_count:
                return 1  # >50% of objects are URIs, so assume mostly use of shared vocabularies
    return 0  # no objects, consider extending the list of properties in reference_data/reference.py


def licensing_score(metadata: Graph, resource: URIRef):
    """Check if the resource has a license.
    If the resource has a license, a score of 2 is given, else a score of 0 is given."""
    license_literals = [
        str(o)
        for (_, _, o) in metadata.triples_choices(
            (resource, data_usage_license_properties, None)
        )
    ]
    value = 0
    if (
        len(license_literals) > 0
    ):  # NB licenses should use a URI, but some use literals. Use of a URI can affect the
        # shared_vocabs_ontologies score under "Interoperatbility".
        value = 2
    return value


def provenance_score(metadata: Graph):
    """Check if the resource has provenance, using common provenance ontologies.
            Currently the following ontologies are checked:
                - PROV
            Additional specific provenance properties
                - see reference_data/reference.py
    If the resource has provenance, a score of 2 is given, else a score of 0 is given."""
    all_props = set(metadata.predicates(subject=None, object=None))
    if any([p for p in all_props if p in PROV]):
        return 2
    elif any([p for p in all_props if p in additional_provenance_properties]):
        return 2
    return 0


def data_source_score(metadata: Graph, resource: URIRef):
    """Check if the resource has a data source, and if so, is provenance for the data source provided.
    If no data source is provided, a score of 2 is given.

    From the DCTERMS ontology for DCTERMS.source: "Best practice is to identify the related resource by means of a URI or a string
    conforming to a formal identification system."
    """
    source_term = metadata.value(
        subject=resource, predicate=DCTERMS.source, object=None
    )
    if not source_term:
        return 0
    elif type(source_term) == URIRef:
        return 2
    elif type(source_term) == Literal and source_term.datatype == XSD.anyURI:
        return 1
    return 0


def searchable_score(metadata: Graph):
    """Check if the resource is searchable"""
    all_props = set(metadata.predicates(subject=None, object=None))
    if any([p for p in all_props if p in searchable_properties]):
        return 1
    return 0
