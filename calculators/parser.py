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
import argparse
import os
from pathlib import Path
from typing import Optional, Union, Tuple

import httpx
from rdflib import Graph, URIRef, BNode, Literal, Namespace
from rdflib.namespace import DCAT, DCTERMS, RDF, TIME
from rdflib.term import Node

from calculators._SCORES import SCORES

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
def _create_parser():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "input",
        help="The path of an RDF file or URL of RDF data online.",
    )

    parser.add_argument(
        "-o",
        "--output",
        help="A path for an output file or an output format. If set to a file path, the output will be written to "
        "the file, rather than returned to standard out. If a format is given, that format will be returned to. "
        "standard out. For a given output file path, the file extension determines the format and must be one "
        f"of {', '.join(RDF_FILE_SUFFIXES.keys())} for Turtle, RDF/XML, JSON-LD or N-Ttripes. "
        f"If a format is given, it must be one of {', '.join(RDF_FILE_SUFFIXES.values())}",
        default="text/turtle",
    )

    parser.add_argument(
        "-v",
        "--validate",
        help="Validate the input with the IDN CP's validator before trying to score it",
        default=False,
    )

    return parser


def _output_is_format(s: str):
    """Checks to see if a string is a known format or a graph"""

    if s in RDF_FILE_SUFFIXES.keys() or s == "graph":
        return True
    else:
        return False


def _get_valid_output_dir(path: Path):
    """Checks that a specified output directory is an existing directory and returns the directory if valid"""

    if not os.path.isdir(path.parent):
        raise argparse.ArgumentTypeError(
            f"The output path you specified, {path}, does not indicate a valid directory"
        )

    return path.parent


def _get_valid_output_file_and_type(path: Path):
    """Checks that a specified output file has a known file type extension and returns it and the corresponding
    RDF Media Type if it is"""

    known_file_types = [".ttl", ".rdf", ".json-ld", ".nt"]
    if path.suffix not in known_file_types:
        raise argparse.ArgumentTypeError(
            f"The output path you specified, {path}, does not specify a known file type. "
            f"It must be one of {', '.join(known_file_types)}"
        )

    return path.name, RDF_FILE_SUFFIXES[path.suffix]


def _input_is_a_file(s: str):
    """Checks if a string is a path to an existing file"""

    if Path(s).is_file():
        return True
    else:
        return False


def _load_input_graph(path_or_url: Union[Path, str]) -> Graph:
    """Parses a file at the path location or download the data from a given URL and returns an RDFLib Graph"""

    g = Graph()
    if _input_is_a_file(path_or_url):
        g.parse(path_or_url)
    else:
        d = httpx.get(path_or_url, follow_redirects=True)
        g.parse(data=d.text, format=d.headers["Content-Type"].split(";")[0])

    return g


def _forward_chain_dcat(g: Graph):
    """Builds out a DCAT graph with RDFS & OWL rules.

    Only builds as necessary for scoring, i.e. not a complete RDFS or OWL inference"""
    for s in g.subjects(RDF.type, DCAT.Dataset):
        g.add((s, RDF.type, DCAT.Resource))

    for s, o in g.subject_objects(DCTERMS.isPartOf):
        g.add((o, DCTERMS.hasPart, s))

    for s, o in g.subject_objects(DCTERMS.hasPart):
        g.add((o, DCTERMS.isPartOf, s))


def _bind_extra_prefixes(g: Graph, prefixes: dict):
    for k, v in prefixes.items():
        g.bind(k, v)


def _create_observation_group(
    resource: URIRef,
    score_class: URIRef,
    beginning: Optional[Literal] = None,
    end: Optional[Literal] = None,
) -> Tuple[Node, Graph]:
    """Creates a Score (ObservationGroup) object to hold multiple Score Dimension measured values (Observations)

    :param resource: The catalogued Resource being scored
    :param score_class: The class of the Score, e.g. scores:FairScore
    :param beginning: A date from which this Score is relevant
    :param end: A date until which this score was relevant
    :return: The ID of the Score and the Score total Graph
    """
    g = Graph()

    g.add((resource, RDF.type, DCAT.Resource))
    score = BNode()
    g.add((resource, SCORES.hasScore, score))
    g.add((score, RDF.type, score_class))
    g.add((score, RDF.type, QB.ObservationGroup))
    g.add((score, SCORES.refResource, resource))

    if beginning is not None or end is not None:
        t = BNode()
        # TODO: decide on the type of Temporal Entity here
        g.add((t, RDF.type, TIME.ProperInterval))
        g.add((score, SCORES.refTime, t))

        if beginning is not None:
            b = BNode()
            g.add((b, RDF.type, TIME.Instant))
            g.add((b, TIME.inXSDDate, beginning))
            g.add((t, TIME.hasBeginning, b))
        if end is not None:
            e = BNode()
            g.add((e, RDF.type, TIME.Instant))
            g.add((e, TIME.inXSDDate, end))
            g.add((t, TIME.hasEnd, e))

    return score, g


def _create_observation(
    score_container: Node, score_property: URIRef, score_value: Union[URIRef, Literal]
) -> Graph:
    """Creates the Observation RDF container for a Score's value for a Resource

    :param resource: the catalogued resource being scored
    :param score_container: the overall Score object (e.g. FAIR for F dimension)
    :param score_property: the Scores Ontology qb:MeasureProperty that defines this score dimension, e.g. scores:fairFScore
    :param score_value: the value of this dimension of the score, e.g. 12 for "F" in FAIR
    :return: a graph of the Observation
    """
    g = Graph()
    obs = BNode()
    g.add((obs, RDF.type, QB.Observation))
    g.add((score_container, QB.observation, obs))

    g.add((obs, score_property, score_value))

    return g
