"""
Calculates the FAIR score of a resource.

usage: fair.py [-h] [-o OUTPUT] [-v VALIDATE] input

positional arguments:
  input                 The path of an RDF file or URL of RDF data online.

options:
  -h, --help            show this help message and exit
  -o OUTPUT, --output OUTPUT
                        A path for an output file or an output format. If set to a file
                        path, the output will be written to the file, rather than returned
                        to standard out. If a format is given, that format will be returned
                        to. standard out. For a given output file path, the file extension
                        determines the format and must be one of .ttl, .rdf, .json-ld, .nt
                        for Turtle, RDF/XML, JSON-LD or N-Triples. If a format is given, it
                        must be one of text/turtle, application/rdf+xml,
                        application/ld+json, text/nt
  -v VALIDATE, --validate VALIDATE
                        Validate the input with the IDN CP's validator before trying to
                        score it
"""
from pathlib import Path
from typing import Optional, Union

import httpx
from pyshacl import validate as val
from rdflib import Graph, URIRef, Namespace, Literal
from rdflib.namespace import DCAT, DCTERMS, PROV, RDF
from rdflib.term import Node

from calculators._SCORES import SCORES
from calculators.functions import (
    machine_readability_score,
    shared_vocabs_ontologies,
    licensing_score,
    provenance_score,
    data_source_score,
)
from calculators.parser import (
    _create_parser,
    _load_input_graph,
    _bind_extra_prefixes,
    _create_observation_group,
    _create_observation,
    _forward_chain_dcat,
    _get_valid_output_dir,
    _get_valid_output_file_and_type,
)

QB = Namespace("http://purl.org/linked-data/cube#")

RDF_FILE_SUFFIXES = {
    ".ttl": "text/turtle",
    ".rdf": "application/rdf+xml",
    ".json-ld": "application/ld+json",
    ".nt": "text/nt",
}

EXTRA_PREFIXES = {
    "scores": SCORES,
    "qb": QB,
}


def calculate_f(metadata: Graph, resource: URIRef, score_container: Node) -> Graph:
    """
    F1. (meta)data are assigned a globally unique and eternally persistent identifier.
    F2. data are described with rich metadata.
    F3. (meta)data are registered or indexed in a searchable resource.
    F4. metadata specify the data identifier.
    """
    f_value = 0
    # from https://ardc.edu.au/resource/fair-data-self-assessment-tool/

    # Does the dataset have any identifiers assigned?
    # 0 No identifier
    # 1 Local identifier
    # 3 Web address (URL)
    # 8 Globally Unique, citable and persistent (e.g. DOI, PURL, ARK or Handle)

    # score will always be 3 or 8 for catalogued resources in RDF
    f_value += 3

    # if the URL is a DOI etc, +1:
    pid_indicators = [
        "doi:",
        "doi.org",
        "ark:",
        "purl.org",
        "linked.data.gov.au",
        "handle.net",
        "w3id.org",
    ]
    for pi in pid_indicators:
        if pi in str(resource):
            f_value += 5
            break

    # TODO: should we test the URL/PID to see if it resolves?

    # Is the dataset identifier included in all metadata records/files describing the data?
    # 0 No
    # 1 Yes

    # always yes for now
    f_value += 1

    # How is the data described with metadata?
    # 0 The data is not described
    # 1 Brief title and description
    # 3 Comprehensively, but in a text-based, non-standard format
    # 4 Comprehensively (see suggestion) using a recognised formal machine-readable metadata schema

    # IDN CP data will always be at least +1 here, +3 if more DCTERMS elements are present other than title & desc,
    # and +4 if all the following are present: title, description, created, modified, type qualifiedAttribution (1+)
    f_value += 1
    c = 0
    for p in metadata.predicates(resource, None):
        if p == DCTERMS.created:
            c += 1
        elif p == DCTERMS.modified:
            c += 1
        elif p == DCTERMS.type:
            c += 1
        elif p == PROV.qualifiedAttribution:
            c += 1
    if c == 1:
        f_value += 1
    elif c == 2:
        f_value += 2
    elif c > 2:
        f_value += 3

    # What type of repository or registry is the metadata record in?
    # 0 The data is not described in any repository
    # 2 Local institutional repository
    # 2 Domain-specific repository
    # 2 Generalist public repository
    # 4 Data is in one place but discoverable through several registries

    # If a catalogue is indicated, +2. If the catalogue responds to a ping for RDF, +4
    catalogue = None
    for o in metadata.objects(resource, DCTERMS.isPartOf):
        catalogue = str(o)
    if catalogue is not None:
        f_value += 2
        RDF_MEDIA_TYPES = [
            "text/turtle",
            "text/n3",
            "application/ld+json",
            "application/n-triples",
            "application/n-quads",
            "application/rdf+xml",
        ]
        try:
            x = httpx.get(
                catalogue,
                headers={"Accept": ", ".join(RDF_MEDIA_TYPES)},
                follow_redirects=True,
            )
            if x.is_success:
                f_value += 2  # changed to maximum of four to align with calculator here https://github.com/au-research/FAIR-Data-Assessment-Tool
        except httpx.HTTPError:
            pass

    return _create_observation(score_container, SCORES.fairFScore, Literal(f_value))


def calculate_a(metadata: Graph, resource: URIRef, score_container: Node) -> Graph:
    """
    A1  (meta)data are retrievable by their identifier using a standardized communications protocol.
    A1.1 the protocol is open, free, and universally implementable.
    A1.2 the protocol allows for an authentication and authorization procedure, where necessary.
    A2 metadata are accessible, even when the data are no longer available.
    """
    a_value = 0

    # How accessible is the data?
    # 0. No access to data or metadata
    # 1. Access to metadata only
    # 2. Unspecified conditional access e.g. contact the data custodian for access
    # 3. Embargoed access after a specified date
    # 4. A de-identified / modified subset of the data is publicly accessible
    # 5. Fully accessible to persons who meet explicitly stated conditions, e.g. ethics approval for sensitive data

    # look for a declared availability classification
    declared = False
    DAR = Namespace("https://linked.data.gov.au/def/data-access-rights/")
    for o in metadata.objects(resource, DCAT.theme):
        declared = True

        # David: scores doubled to align with https://github.com/au-research/FAIR-Data-Assessment-Tool/
        if o in [DAR.protected, DAR.restricted]:
            a_value += 0
        elif o == DAR["metadata-only"]:
            a_value += 2
        elif o == DAR.conditional:
            a_value += 4
        elif o == DAR.embargoed:
            a_value += 6
        # 4
        elif o == DAR.open:
            a_value += 10

    if not declared:
        # TODO: try some other method
        pass

    # Is the data available online without requiring specialised protocols or tools once access has been approved?
    # 0. No access to data
    # 1. By individual arrangement
    # 2. File download from online location
    # 3. Non-standard web service (e.g. OpenAPI/Swagger/informal API)
    # 4. Standard web service API (e.g. OGC)

    return _create_observation(score_container, SCORES.fairAScore, Literal(a_value))


def calculate_i(metadata: Graph, resource: URIRef, score_container: Node) -> Graph:
    """
    ... describe function inputs/outputs ...

    I score notes:
    I1. (meta)data use a formal, accessible, shared, and broadly applicable language for knowledge representation.
    I2. (meta)data use vocabularies that follow FAIR principles.
    I3. (meta)data include qualified references to other (meta)data.

    additionally ..

    3. Data Objects can be Interoperable only if:
    3.1. (Meta) data is machine-actionable [8]
        [8] in eScience, machine-readability of data is imminent. Metadata being machine readable is a conditio sine qua
         non for FAIRness. Having the actual data elements also machine-readable will make the Data Object of a higher
         level of interoperability and makes functional interlinking and analysis in broader context much easier, but it
         is not a pre-condition for FAIR data publishing. Some data elements, for instance images and ‘raw data’ can not
         always be made machine-processable. Being published with FAIR metadata is of very high value in its own right.

    3.2. (Meta) data formats utilize shared vocabularies and/or ontologies [9]
        [9] When the use of community adopted and public terminology systems is not possible, for instance for reasons
        described in explanatory note 5, or because the Data Objects contain concepts that have not yet been described
        in any public vocabulary or ontology known to the provider, the provider should nevertheless try to create a
        term vocabulary of their own and publish it publicly and openly, preferably in a machine-readable form. The
        vocabulary or ontology that constrains each constrained data field should be unambiguously identified either by
        the field itself or by the associated Data Object metadata. For non-constrained fields, whenever possible the
        value-type of the field should be annotated using a publicly-accessible vocabulary or ontology. This annotation
        should be clear in the Data Object metadata.

    3.3  (Meta) data within the Data Object should thus be both syntactically parseable and semantically
    machine-accessible [10]
        [10] Both syntax and semantics of data models and formats used for (Meat) data in Data Objects should be easy to
        identify and use, parse or translate by machines. As in the case of identifier schemes and vocabularies, a wide
        variety of data formats (ranging from URI-featuring spread-sheets such as RightField or OntoMaton to rich RDF) can
        be principally FAIR. It is obvious that any parsing and translation protocol is error-prone and the ideal situation
        is to restrict FAIR data publishing to as few community adopted formats and standards as possible. However, if a
        provider can prove that an alternative data model/format is unambiguously parsable to one of the community adopted
        FAIR formats, there is no particular reason why such a format could not be considered FAIR. Some data types may
        simply be not ‘capturable’ in one of the existing formats, and in that case maybe only part of the data elements can
        be parsed. FAIRports will increasingly offer guidance and assistance in such cases.
    """
    i_value = 0
    # 3.1 is the *data* machine-readable?
    i_value += machine_readability_score(metadata, resource)
    # 3.1 the metadata is assumed machine-readable in order to use this tool
    i_value += 2
    # 3.2 "(Meta) data formats utilize shared vocabularies and/or ontologies"
    i_value += shared_vocabs_ontologies(metadata, resource)
    # 3.3 "(Meta) data within the Data Object should thus be both syntactically parseable and semantically machine-accessible"
    # If the data is both machine-readable and uses shared vocabularies and/or ontologies, then it *should* also be parseable
    # and machine-accessible.
    # The total possible score for the data machine readability and shared vocabularies and/or ontologies is 4, if at
    # least 3 points are scored, a further 2 points are added, if at least 1 point is scored, a further 1 point is added.
    i_value_ignoring_metadata = i_value - 2
    if i_value_ignoring_metadata >= 3:
        i_value += 2
    elif i_value_ignoring_metadata >= 1:
        i_value += 2

    return _create_observation(score_container, SCORES.fairIScore, Literal(i_value))


def calculate_r(metadata: Graph, resource: URIRef, score_container: Node) -> Graph:
    """
    R1. (meta)data have a plurality of accurate and relevant attributes.
    R1.1. (meta)data are released with a clear and accessible data usage license.
    R1.2. (meta)data are associated with their provenance.
    R1.3. (meta)data meet domain-relevant community standards.

    4. For Data Objects to be Re-usable additional criteria are:
        4.1 Data Objects should be compliant with principles 1-3
        4.2 (Meta) data should be sufficiently well-described and rich that it can be automatically (or with minimal
        human effort) linked or integrated, like-with-like, with other data sources [11 and JDDCP 7 and JDDCP 8]
        4.3 Published Data Objects should refer to their sources with rich enough metadata and provenance to enable
        proper citation (ref to JDDCP 1-3).

    JDDCP 1-3:
        1. Importance
        Data should be considered legitimate, citable products of research. Data citations should be accorded the same
        importance in the scholarly record as citations of other research objects, such as publications[1].
        2. Credit and Attribution
        Data citations should facilitate giving scholarly credit and normative and legal attribution to all contributors
         to the data, recognizing that a single style or mechanism of attribution may not be applicable to all data[2].
        3. Evidence
        In scholarly literature, whenever and wherever a claim relies upon data, the corresponding data should be cited[3].

    David comment: Assume R1. / 4.1 is referring to "F", "A" and "I" principles. As these are scored separately it would be duplicative
    to score them again here (?).
    """
    r_value = 0
    # R1.1. "(meta)data are released with a clear and accessible data usage license."
    r_value += licensing_score(metadata, resource)  # max score is 2
    # R1.2. "(meta)data are associated with their provenance."
    # Assume provenance is declared through the use of a standard set of properties, such those in the provenance
    # ontology
    r_value += provenance_score(metadata)  # max score is 3
    # R1.3. "(meta)data meet domain-relevant community standards."
    # interpreted as referring to 4.3, which in turn refers to JDDCP 1-3.
    # This has been interpreted that, if a dcterms:source is declared, it should ideally be a URI,
    # and additional provenance information for it should exist.
    # logic implemented: if a dcterms:source is declared, check its type: if URI 2 points, otherwise, if it is a literal
    # AND has a datatype of xsd:anyURI, 1 point, otherwise 0 points.
    r_value += data_source_score(metadata, resource)  # max score is 2

    return _create_observation(score_container, SCORES.fairRScore, Literal(r_value))


def calculate_fair(g: Graph, resource: URIRef) -> Graph:
    s = Graph(bind_namespaces="rdflib")
    _bind_extra_prefixes(s, EXTRA_PREFIXES)

    og_node, og_graph = _create_observation_group(resource, SCORES.FairScore)
    s += og_graph

    s += calculate_f(g, resource, og_node)
    s += calculate_a(g, resource, og_node)
    s += calculate_i(g, resource, og_node)
    s += calculate_r(g, resource, og_node)

    return s


def calculate_fair_per_resource(g: Graph) -> Graph:
    scores = Graph(bind_namespaces="rdflib")
    _bind_extra_prefixes(scores, EXTRA_PREFIXES)

    for r in g.subjects(RDF.type, DCAT.Resource):
        scores += calculate_fair(g, r)  # type: ignore

    return scores


def normalise_fair_scores(g: Graph) -> Graph:
    """
    Normalizes FAIR scores to a range between 0 and 1, where 0 is the lowest possible score and 1 is the highest
    possible score.
    """
    for s in g.subjects(SCORES.hasScore, None):
        og_node, og_graph = _create_observation_group(s, SCORES.FairScoreNormalised)
        f_value = next(g.objects(subject=None, predicate=SCORES.fairFScore))
        a_value = next(g.objects(subject=None, predicate=SCORES.fairAScore))
        i_value = next(g.objects(subject=None, predicate=SCORES.fairIScore))
        r_value = next(g.objects(subject=None, predicate=SCORES.fairRScore))
        g += _create_observation(
            og_node, SCORES.fairFScoreNormalised, Literal(f"{int(f_value) / 17:.2f}")
        )
        g += _create_observation(
            og_node, SCORES.fairAScoreNormalised, Literal(f"{int(a_value) / 10:.2f}")
        )
        g += _create_observation(
            og_node, SCORES.fairIScoreNormalised, Literal(f"{int(i_value) / 8:.2f}")
        )
        g += _create_observation(
            og_node, SCORES.fairRScoreNormalised, Literal(f"{int(r_value) / 7:.2f}")
        )
        g.add((og_node, RDF.type, SCORES.FairScoreNormalised))
        g.add((og_node, RDF.type, QB.ObservationGroup))
        g.add((og_node, SCORES.refResource, s))
        g.add((s, SCORES.hasScore, og_node))
    return g


def main(
    input: Union[Path, str, Graph],
    output: Optional[str] = "text/turtle",
    validate: bool = False,
):
    """The main function of this module. Accepts a path to an RDF file, a URL leading to RDF or an RDFLib graph
    as input and returns either an RDFLib Graph object, an RDF stream in the given format or writes RDF to a file with
    format specified by file ending"""

    # load input
    if isinstance(input, Graph):
        g = input
    else:
        g = _load_input_graph(input)

    # build out input
    _forward_chain_dcat(g)

    # TODO point to https://data.idnau.org/pid/cp/validator.ttl as validator.

    # validate
    if validate:
        validator = Path(__file__).parent.parent.absolute().parent / "validator.ttl"
        conforms, report_graph, report_text = val(g, shacl_graph=str(validator))
        if not conforms:
            raise ValueError(
                f"Input is not valid IDN CP. Validation errors are:\n{report_text}"
            )

    # calculate
    scores = calculate_fair_per_resource(g)

    norm_scores = normalise_fair_scores(scores)

    scores += norm_scores

    # generate output
    # std out
    if output in RDF_FILE_SUFFIXES.values():
        if output == "application/ld+json":
            jsonld_context = {
                "@vocab": "https://linked.data.gov.au/def/scores/",
                "dcat": "http://www.w3.org/ns/dcat#",
                "qb": "http://purl.org/linked-data/cube#",
                "time": "http://www.w3.org/2006/time#",
                "xsd": "http://www.w3.org/2001/XMLSchema#",
            }

            # adding all prefixes bound to the graph to the JSON-LD context seems not to work
            # for prefix, namespace in scores.namespace_manager.namespaces():
            #     jsonld_context[prefix] = namespace

            print(
                scores.serialize(
                    format=output, indent=4, context=jsonld_context, auto_compact=True
                )
            )
        else:
            print(
                scores.serialize(
                    format="longturtle" if output == "text/turtle" else output
                )
            )
    # write to file
    elif output.endswith(tuple(RDF_FILE_SUFFIXES.keys())):
        p = Path(output)
        output_dir = _get_valid_output_dir(p)
        output_file, output_format = _get_valid_output_file_and_type(p)
        return scores.serialize(
            destination=p,
            format="longturtle" if output_format == "text/turtle" else output_format,
        )
    # return Graph object
    else:
        return scores


if __name__ == "__main__":
    args = _create_parser().parse_args()

    main(args.input, args.output, args.validate)
