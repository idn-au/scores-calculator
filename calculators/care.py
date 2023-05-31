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
from rdflib import Graph, URIRef, Namespace, Literal, DCTERMS
from rdflib.namespace import DCAT, RDF
from rdflib.term import Node

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


def calculate_care_c(metadata: Graph, resource: URIRef, score_container: Node) -> Graph:
    """ """
    c_value = 0
    c1_score = calculate_care_c1(metadata, resource)
    c_value += c1_score
    c_value += calculate_care_c2(metadata, resource, c1_score)

    return _create_observation(score_container, SCORES.careCScore, Literal(c_value))


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
    c1_value += calculate_c1_discoverable(metadata, resource)
    c1_value += calculate_c1_searchable(metadata)
    c1_value += calculate_c1_accessible(metadata, resource)
    return c1_value


def calculate_c1_discoverable(metadata: Graph, resource: URIRef):
    """Metadata is discoverable (+1)"""
    catalogue = None
    for o in metadata.objects(resource, DCTERMS.isPartOf):
        catalogue = str(o)
    if catalogue is not None:
        RDF_MEDIA_TYPES = [
            "text/turtle",
            "text/n3",
            "application/ld+json",
            "application/n-triples",
            "application/n-quads",
            "application/rdf+xml",
        ]
        x = httpx.get(
            catalogue,
            headers={"Accept": ", ".join(RDF_MEDIA_TYPES)},
            follow_redirects=True,
        )
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
    if c1_score > 2:
        c2_value += 1


def calculate_c1_accessible(metadata: Graph, resource: URIRef):
    """Data is accessible (restrictions can apply) (Access Rights exist,+1)"""
    if any(metadata.objects(resource, DCTERMS.accessRights)):
        return 1
    return 0


def calculate_care_a(metadata: Graph, resource: URIRef, score_container: Node) -> Graph:
    """ """
    a_value = 0
    return _create_observation(score_container, SCORES.careAScore, Literal(a_value))


def calculate_care_r(metadata: Graph, resource: URIRef, score_container: Node) -> Graph:
    """ """
    r_value = 0
    return _create_observation(score_container, SCORES.careRScore, Literal(r_value))


def calculate_care_e(metadata: Graph, resource: URIRef, score_container: Node) -> Graph:
    """ """
    e_value = 0
    return _create_observation(score_container, SCORES.careEScore, Literal(e_value))


def calculate_care(g: Graph, resource: URIRef) -> Graph:
    s = Graph(bind_namespaces="rdflib")
    _bind_extra_prefixes(s, EXTRA_PREFIXES)

    og_node, og_graph = _create_observation_group(resource, SCORES.careScore)
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
