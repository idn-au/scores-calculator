from rdflib.namespace import DCAT, DCTERMS, PROV, RDFS


properties_for_mediatypes_formats = [DCTERMS.format, DCAT.mediaType]

# mime types / file extensions considered machine-readable
# used for interoperability scoring 3.1
machine_readable_formats_to_mime_types = {
    "json": "application/json",
    "xml": "application/xml",
    "csv": "text/csv",
    "tsv": "text/tab-separated-values",
    "yaml": "application/x-yaml",
    "yml": "application/x-yaml",
    "rdf": "application/rdf+xml",
    "ttl": "text/turtle",
    "jsonld": "application/ld+json",
    "geojson": "application/geo+json",
    "gml": "application/gml+xml",
    "kml": "application/vnd.google-earth.kml+xml",
    "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",  # Excel
    "xls": "application/vnd.ms-excel",  # Excel
    "ods": "application/vnd.oasis.opendocument.spreadsheet",  # ODF
}

# used in interoperability scoring, for 3.2
properties_expected_to_have_objects_with_uris = [
    DCTERMS.format,
    DCTERMS.type,
    DCTERMS.license,
    DCTERMS.publisher,
    DCTERMS.creator,
    DCTERMS.contributor,
    DCTERMS.accessRights,
    PROV.agent,
    PROV.hadRole,
    DCAT.hadRole,
    DCAT.theme,
    RDFS.member,
]

# used in Re-usability scoring for R1.1
data_usage_license_properties = [DCTERMS.license]

# used in Re-usability scoring for R1.2
additional_provenance_properties = [DCTERMS.source]
