"""
Calculates the care score of a resource.

usage: care.py [-h] [-o OUTPUT] [-v VALIDATE] input

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
from rdflib import Graph, URIRef, Namespace, Literal, DCTERMS, PROV, RDFS, SKOS
from rdflib.namespace import DCAT, RDF
from rdflib.term import Node, BNode

from calculators._SCORES import SCORES
from calculators.functions import searchable_score
from calculators.parser import (
    _create_parser,
    _load_input_graph,
    _bind_extra_prefixes,
    _create_observation_group,
    _create_observation,
    _forward_chain_dcat,
    _get_valid_output_dir,
    _get_valid_output_file_and_type,
    _forward_chain_labels,
    _forward_chain_descriptions,
)

QB = Namespace("http://purl.org/linked-data/cube#")

RDF_MEDIA_TYPES = [
    "text/turtle",
    "text/n3",
    "application/ld+json",
    "application/n-triples",
    "application/n-quads",
    "application/rdf+xml",
]

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


def calculate_care_c(
    metadata: Graph, resource: URIRef, score_container: Node, val_only=False
) -> Graph | int:
    """Collective benefit

    Data ecosystems shall be designed and function in ways that enable Indigenous Peoples to derive benefit from the
    data."""
    #TODO obsv_g = Graph()
    c_value = 0
    c1_score = calculate_care_c1(metadata, resource)  # max 3
    #TODO obsv_g += _create_observation(score_container, SCORES.careC1Score, Literal(c1_score))
    c_value += c1_score
    c2_score = calculate_care_c2(metadata, resource, c1_score)  # max 3
    c_value += c2_score
    c_value += calculate_care_c3(metadata, resource, c2_score)  # max 2
    if not val_only:
        return _create_observation(score_container, SCORES.careCScore, Literal(c_value))
    return c_value


def calculate_care_c1(metadata: Graph, resource: URIRef) -> int:
    """
    For inclusive development and innovation

    Governments and institutions must actively support the use and reuse of data by Indigenous nations and communities by facilitating the establishment of the foundations for Indigenous innovation, value generation, and the promotion of local self-determined development processes.

    Interpretation:
    Max score of 3.
    Metadata is discoverable (+1)
    Searchable (+1)
    Data is accessible (restrictions can apply) (Access Rights exist,+1)
    """
    c1_value = 0
    c1_value += calculate_c1_discoverable(resource)
    c1_value += calculate_c1_searchable(metadata)
    c1_value += calculate_c1_accessible(metadata, resource)
    return c1_value


def calculate_c1_discoverable(resource: URIRef):
    """check if the resource itself is discoverable"""
    try:
        x = httpx.get(
            resource,
            follow_redirects=True,
        )
    except httpx.HTTPError:
        return 0
    if x.is_success:
        return 1
    return 0


def calculate_c1_searchable(metadata: Graph):
    """Searchable (+1)"""
    return searchable_score(metadata)


def calculate_care_c2(metadata: Graph, resource: URIRef, c1_score) -> int:
    """For improved governance and citizen engagement

    Data enrich the planning, implementation, and evaluation processes that support the service and policy needs of
    Indigenous communities. Data also enable better engagement between citizens, institutions, and governments to
    improve decision-making. Ethical use of open data has the capacity to improve transparency and decision-making by
    providing Indigenous nations and communities with a better understanding of their peoples, territories, and
    resources. It similarly can provide greater insight into third-party policies and programs affecting Indigenous
    Peoples.

    C1>2,
    Data catalogue is discoverable (+1)
    (Ethical) Use of the data has been documented (Title exists, +1)
    Description exists, +1
    """
    c2_value = 0
    if c1_score > 2 and calculate_c2_discoverable(metadata, resource) == 1:
        c2_value += 1
    c2_value += any(metadata.objects(resource, RDFS.label))
    c2_value += any(metadata.objects(resource, DCTERMS.description))
    return c2_value


def calculate_care_c3(metadata: Graph, resource: URIRef, c2_score: int) -> int:
    """For equitable outcomes

    Indigenous data are grounded in community values, which extend to society at large. Any value created from
    Indigenous data should benefit Indigenous communities in an equitable manner and contribute to Indigenous
    aspirations for wellbeing.

    (Ethical) Use of the data has been documented [C2>2, +1] and then
    locations of data collected are discoverable (Distribution info exists, +1).
    Equitable Outcomes from data are discoverable,? If the catalogue is about the data, I am not sure how provenance can
    be measured.
    """
    c3_value = 0
    if c2_score > 2:
        c3_value += 1
    c3_value += any(metadata.objects(resource, DCAT.distribution))
    # TODO determine how to measure equitable outcomes.
    return c3_value


def calculate_c2_discoverable(metadata: Graph, resource: URIRef):
    """Metadata is discoverable (+1)"""
    catalogue = None
    for o in metadata.objects(resource, DCTERMS.isPartOf):
        if isinstance(o, BNode):
            catalogue = str(metadata.value(o, PROV.entity))
        else:
            catalogue = str(o)
        if catalogue is not None:
            try:
                x = httpx.get(
                    catalogue,
                    follow_redirects=True,
                )
            except httpx.HTTPError:
                return 0
            if x.is_success:
                return 1
    return 0


def calculate_c1_accessible(metadata: Graph, resource: URIRef):
    """Data is accessible (restrictions can apply) (Access Rights exist,+1)"""
    if any(metadata.objects(resource, DCTERMS.accessRights)):
        return 1
    return 0


def calculate_care_a(
    metadata: Graph, resource: URIRef, score_container: Node, val_only=False
) -> Graph | int:
    """Authority to control

    Indigenous Peoples’ rights and interests in Indigenous data must be recognised and their authority to control such
    data be empowered. Indigenous data governance enables Indigenous Peoples and governing bodies to determine how
    Indigenous Peoples, as well as Indigenous lands, territories, resources, knowledges and geographical indicators, are
    represented and identified within data."""
    a_value = 0
    a1_score = calculate_care_a1(metadata, resource)  # max 3
    a_value += a1_score
    a2_score = calculate_care_a2(metadata, resource, a1_score)  # max 3
    a_value += a2_score
    a3_score = calculate_care_a3(metadata, resource, a2_score)  # max 3
    a_value += a3_score
    if not val_only:
        return _create_observation(score_container, SCORES.careAScore, Literal(a_value))
    return a_value


def calculate_care_a1(metadata: Graph, resource: URIRef) -> int:
    """Recognizing rights and interests

    Indigenous Peoples have rights and interests in both Indigenous Knowledge and Indigenous data. Indigenous Peoples
    have collective and individual rights to free, prior, and informed consent in the collection and use of such data,
    including the development of data policies and protocols for collection.

    A1.1     The Institutional Data Catalogue has applied Institutional discovery Notices.
    [Attribution Incomplete Notice exists (+1)] and/or [Open to Collaboration Notice exists (+1)]

    A1.2      Licence, Rights and Access Rights are complete, +2
    """
    a1_value = 0
    a1_value += calculate_a11_notices(metadata, resource)
    a1_value += calculate_a12_licence_rights(metadata, resource)
    return a1_value


def calculate_a11_notices(metadata: Graph, resource: URIRef):
    """The Institutional Data Catalogue has applied Institutional discovery Notices.
    [Attribution Incomplete Notice exists (+1)] and/or [Open to Collaboration Notice exists (+1)]"""
    # TODO create reference set of notices - we will add e.g. help wanted notice
    IN = Namespace("http://data.idnau.org/pid/vocab/lc-in/")
    if any(metadata.triples((resource, None, IN["attribution-incomplete"]))) or any(
        metadata.triples((resource, None, IN["open-to-collaborate"]))
    ):
        return 1
    return 0


def calculate_a12_licence_rights(metadata: Graph, resource: URIRef):
    """A1.2      Licence, Rights and Access Rights are complete, +2"""
    if (
        any(metadata.objects(resource, DCTERMS.rights))
        or any(metadata.objects(resource, DCTERMS.license))
        or any(metadata.objects(resource, DCTERMS.accessRights))
    ):
        return 2
    return 0


def calculate_care_a2(metadata: Graph, resource: URIRef, a1_score) -> int:
    """Data for governance

    Indigenous Peoples have the right to data that are relevant to their world views and empower self-determination and
    effective self-governance. Indigenous data must be made available and accessible to Indigenous nations and
    communities in order to support Indigenous governance.

    The Institutional Data Catalogue is informed by an Indigenous Data Governance framework [Data Governance Framework
    is catalogued and associated with the metadata records (+2)] and
    has applied Institutional discovery/attribution Notices.[A1>0, +1]
    """
    a2_score = 0
    if a1_score > 0:
        a2_score += 1
    a2_score += calculate_data_governance_framework(metadata, resource)
    return a2_score


def calculate_data_governance_framework(metadata: Graph, resource: URIRef):
    gov_score = 0
    potential_catalogs = metadata.objects(resource, DCTERMS.isPartOf)
    for catalog in potential_catalogs:
        potential_governance_frameworks = metadata.objects(catalog, DCTERMS.hasPart)
        for framework in potential_governance_frameworks:
            framework_labels = metadata.objects(framework, RDFS.label)
            for label in framework_labels:
                if "governance" in label.lower() and "indigenous" in label.lower():
                    gov_score += 2
                    return gov_score
    return gov_score


def calculate_care_a3(metadata: Graph, resource: URIRef, a2_score) -> int:
    """Governance of data

    Indigenous Peoples have the right to develop cultural governance protocols for Indigenous data and be active leaders
    in the stewardship of, and access to, Indigenous data especially in the context of Indigenous Knowledge.

    The Institutional Data Catalogue is informed by an Indigenous Data Governance framework [A2.1>0, and…] with an
    identified Indigenous Data Steward and/or Data Custodian.
    [...IDN Role Codes have Agents+ Organisations Indigeneity NOT EQUAL TO Non-Indigenous OR Indigeneity Unknown] (+3)
    """
    a32_score = calculate_a32_score(metadata, resource)
    if a2_score > 0 and a32_score:
        return 3
    return 0


def calculate_a32_score(metadata: Graph, resource: URIRef):
    if org_indigeneity(metadata, resource) or ind_indigeneity(metadata, resource):
        return True
    return False


def org_indigeneity(metadata: Graph, resource: URIRef):
    ORG_INDIG = Namespace("https://data.idnau.org/pid/vocab/org-indigeneity/")
    org_role_codes = [
        ORG_INDIG["owned-by-indigenous-persons"],
        ORG_INDIG["indigenous-persons-organisation"],
        ORG_INDIG["run-by-indigenous-persons"],
    ]
    qualified_attribution_bns = metadata.objects(resource, PROV.qualifiedAttribution)
    for qabn in qualified_attribution_bns:
        for role in metadata.objects(qabn, DCAT.hadRole):
            if role in org_role_codes:
                return True
    return False


def ind_indigeneity(metadata: Graph, resource: URIRef):
    IND_INDIG = Namespace("https://data.idnau.org/pid/vocab/indigeneity/")
    ind_role_codes = [
        IND_INDIG["by-indigenous-people"],
    ]
    qualified_attribution_bns = metadata.objects(resource, PROV.qualifiedAttribution)
    for qabn in qualified_attribution_bns:
        for role in metadata.objects(qabn, DCAT.hadRole):
            if role in ind_role_codes:
                return True
    return False


def calculate_care_r(metadata: Graph, resource: URIRef, score_container: Node) -> Graph:
    """
    Those working with Indigenous data have a responsibility to share how those data are used to support Indigenous
    Peoples’ self determination and collective benefit. Accountability requires meaningful and openly available evidence
    of these efforts and the benefits accruing to Indigenous Peoples.

    """
    r_value = 0
    r1_value = calculate_r1(metadata, resource)  # max 3
    r_value += r1_value
    r2_value = calculate_r2(metadata, resource)  # max 0
    r_value += r2_value
    r3_value = calculate_r3(metadata, resource)  # max 6
    r_value += r3_value
    return _create_observation(score_container, SCORES.careRScore, Literal(r_value))


def calculate_r1(metadata: Graph, resource: URIRef):
    """
    For positive relationships

    Indigenous data use is unviable unless linked to relationships built on respect, reciprocity, trust, and mutual
    understanding, as defined by the Indigenous Peoples to whom those data relate. Those working with Indigenous data
    are responsible for ensuring that the creation, interpretation, and use of those data uphold, or are respectful of,
    the dignity of Indigenous nations and communities.

    [A1.1>0, and A1.2>2, and A3.2>0, +3]
    """
    a11_value = calculate_a11_notices(metadata, resource)
    a12_value = calculate_a12_licence_rights(metadata, resource)
    a32_value = calculate_a32_score(metadata, resource)
    if a11_value > 0 and a12_value > 1 and a32_value:
        return 3
    return 0


def calculate_r2(metadata: Graph, resource: URIRef) -> int:
    """
    For expanding capability and capacity

    Use of Indigenous data invokes a reciprocal responsibility to enhance data literacy within Indigenous communities
    and to support the development of an Indigenous data workforce and digital infrastructure to enable the creation,
    collection, management, security, governance, and application of data.
    """
    # TODO - we don't believe this can be calculated at present.
    return 0


def calculate_r3(metadata: Graph, resource: URIRef) -> int:
    """
    For Indigenous languages and worldviews
    Resources must be provided to generate data grounded in the languages, worldviews, and lived experiences (including
    values and principles) of Indigenous Peoples.

    The Institutional Data Catalogue is informed by an Indigenous Data Governance framework [Data Governance Framework
    is catalogued, +1 (and associated with the metadata records, +1)]
    with an identified Indigenous Custodian [organisation has indigeneity +1, individual has indigeneity +1. Using
    vocabs]
    working with the ID Steward.
    Provenance, Protocols and Permissions labels have been negotiated and applied.
    [C1 > 0 and C2 > 0 and C3 > 0 and A1 > 0 and A2 > 0 and A3 > 0, +3]

    """
    r3_score = 0
    gov_fwork = calculate_data_governance_framework(metadata, resource)
    if gov_fwork > 0:
        r3_score += 1
    r3_score += org_indigeneity(metadata, resource)
    r3_score += ind_indigeneity(metadata, resource)

    c1_score = calculate_care_c1(metadata, resource)
    c2_score = calculate_care_c2(metadata, resource, c1_score)
    c3_score = calculate_care_c3(metadata, resource, c2_score)

    a1_score = calculate_care_a1(metadata, resource)
    a2_score = calculate_care_a2(metadata, resource, a1_score)
    a3_score = calculate_care_a3(metadata, resource, a2_score)

    if (
        c1_score > 0
        and c2_score > 0
        and c3_score > 0
        and a1_score > 0
        and a2_score > 0
        and a3_score > 0
    ):
        r3_score += 3
    return r3_score


def calculate_care_e(metadata: Graph, resource: URIRef, score_container: Node) -> Graph:
    """
    Ethics

    Indigenous Peoples’ rights and wellbeing should be the primary concern at all stages of the data life cycle and
    across the data ecosystem
    """
    e_value = 0
    e1_value = calculate_e1(metadata, resource)
    e_value += e1_value
    return _create_observation(score_container, SCORES.careEScore, Literal(e_value))


def calculate_e1(metadata: Graph, resource: URIRef) -> int:
    """For minimizing harm and maximizing benefit

    Ethical data are data that do not stigmatize or portray Indigenous Peoples, cultures, or knowledges in terms of
    deficit. Ethical data are collected and used in ways that align with Indigenous ethical frameworks and with rights
    affirmed in UNDRIP. Assessing ethical benefits and harms should be done from the perspective of the Indigenous
    Peoples, nations, or communities to whom the data relate.

    (Ethical (re)) Use of the data are clearly defined and accessible.
    [C1 > 1 and C2 > 1 and C3 > 1, A1>1, A2>1 +3]
    """
    c1_value = calculate_care_c1(metadata, resource)
    c2_value = calculate_care_c2(metadata, resource, c1_value)
    c3_value = calculate_care_c3(metadata, resource, c2_value)
    a1_value = calculate_care_a1(metadata, resource)
    a2_value = calculate_care_a2(metadata, resource, a1_value)

    if c1_value > 1 and c2_value > 1 and c3_value > 1 and a1_value > 1 and a2_value > 1:
        return 3
    return 0


def calculate_e2(metadata: Graph, resource: URIRef) -> int:
    """
    For justice

    Ethical processes address imbalances in power, resources, and how these affect the expression of Indigenous rights
    and human rights. Ethical processes must include representation from relevant Indigenous communities.

    Ethical (re)use of the data are clearly defined, accessible and
    have an Indigenous Data Steward or Custodian identified.[E1>2, A3.2>1, +3]
    """
    e1_value = calculate_e1(metadata, resource)
    a32_value = calculate_a32_score(metadata, resource)
    if e1_value > 2 and a32_value:
        return 3
    return 0


def calculate_e3(metadata: Graph, resource: URIRef) -> int:
    """
    For future use

    Data governance should take into account the potential future use and future harm based on ethical frameworks
    grounded in the values and principles of the relevant Indigenous community. Metadata should acknowledge the
    provenance and purpose and any limitations or obligations in secondary use inclusive of issues of consent.

    Ethical (re)use of the data are clearly defined and
     have an Indigenous Steward or Custodian identified
     within an identified Indigenous Data Governance Framework.
    Provenance, Protocols and Permissions labels have been negotiated and applied.
    [E2>2, A2>1, A1>2, +3]
    """
    e2_value = calculate_e2(metadata, resource)
    a1_value = calculate_care_a1(metadata, resource)
    a2_value = calculate_care_a2(metadata, resource, a1_value)
    if e2_value > 2 and a1_value > 2 and a2_value > 1:
        return 3
    return 0


def calculate_care(g: Graph, resource: URIRef) -> Graph:
    s = Graph(bind_namespaces="rdflib")
    _bind_extra_prefixes(s, EXTRA_PREFIXES)

    og_node, og_graph = _create_observation_group(resource, SCORES.CareScore)
    s += og_graph

    s += calculate_care_c(g, resource, og_node)
    s += calculate_care_a(g, resource, og_node)
    s += calculate_care_r(g, resource, og_node)
    s += calculate_care_e(g, resource, og_node)

    return s


def calculate_care_per_resource(g: Graph) -> Graph:
    scores = Graph(bind_namespaces="rdflib")
    _bind_extra_prefixes(scores, EXTRA_PREFIXES)

    for r in g.subjects(RDF.type, DCAT.Resource):
        scores += calculate_care(g, r)  # type: ignore

    return scores


def normalise_care_scores(g: Graph) -> Graph:
    """Normalizes CARE scores to a range between 0 and 1, where 0 is the lowest possible score and 1 is the highest"""
    for s in g.subjects(SCORES.hasScore, None):
        og_node, og_graph = _create_observation_group(s, SCORES.CareScoreNormalised)
        c_value = next(g.objects(subject=None, predicate=SCORES.careCScore))
        a_value = next(g.objects(subject=None, predicate=SCORES.careAScore))
        r_value = next(g.objects(subject=None, predicate=SCORES.careRScore))
        e_value = next(g.objects(subject=None, predicate=SCORES.careEScore))
        g += _create_observation(
            og_node, SCORES.careCScoreNormalised, Literal(f"{int(c_value) / 8:.2f}")
        )
        g += _create_observation(
            og_node, SCORES.careAScoreNormalised, Literal(f"{int(a_value) / 9:.2f}")
        )
        g += _create_observation(
            og_node, SCORES.careRScoreNormalised, Literal(f"{int(r_value) / 9:.2f}")
        )
        g += _create_observation(
            og_node, SCORES.careEScoreNormalised, Literal(f"{int(e_value) / 3:.2f}")
        )
        g.add((og_node, RDF.type, SCORES.CareScoreNormalised))
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
    _forward_chain_labels(g)
    _forward_chain_descriptions(g)

    # validate
    if validate:
        validator = Path(__file__).parent.parent.absolute().parent / "validator.ttl"
        conforms, report_graph, report_text = val(g, shacl_graph=str(validator))
        if not conforms:
            raise ValueError(
                f"Input is not valid IDN CP. Validation errors are:\n{report_text}"
            )

    # calculate
    scores = calculate_care_per_resource(g)

    norm_scores = normalise_care_scores(scores)

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
