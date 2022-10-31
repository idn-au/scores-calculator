"""
Calculates the FAIR, CARE, LC Labels or other score of a resource.

usage: calculators [-h] [-s {f,c,l,a}] [-o OUTPUT] [-v VALIDATE] input

positional arguments:
  input                 The path of an RDF file or URL of RDF data online.

options:
  -h, --help            show this help message and exit
  -s {f,c,l,a}, --score {f,c,l,a}
                        Which score to calculate. Options are f (FAIR), c (CARE), l (LC Labels), a (all)
  -o OUTPUT, --output OUTPUT
                        A path for an output file or an output format. If set to a file path, the output will be written to the file, rather than returned to standard out. If a format is
                        given, that format will be returned to. standard out. For a given output file path, the file extension determines the format and must be one of .ttl, .rdf, .json-ld,
                        .nt for Turtle, RDF/XML, JSON-LD or N-Ttripes. If a format is given, it must be one of text/turtle, application/rdf+xml, application/ld+json, text/nt
  -v VALIDATE, --validate VALIDATE
                        Validate the input with the IDN CP's validator before trying to score it
"""
import argparse
import os
from pathlib import Path
from typing import Optional, Union, Tuple

import httpx
from pyshacl import validate as val
from rdflib import Graph, URIRef, BNode, Namespace, Literal
from rdflib.namespace import DCAT, DCTERMS, PROV, RDF, TIME
from rdflib.term import Node

import fair


from _SCORES import SCORES

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
        "-s",
        "--score",
        help="Which score to calculate. Options are f (FAIR), c (CARE), l (LC Labels), a (all)",
        choices=["f", "c", "l", "a"],
        default="f",
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


if __name__ == "__main__":
    args = _create_parser().parse_args()

    if args.score == "f":
        fair.main(args.input, args.output, args.validate)
    # elif args.score == "c": TODO: implement
    #     care.main(args.input, args.output, args.validate)
    # elif args.score == "l": TODO: implement
    #     lclabels.main(args.input, args.output, args.validate)
    elif args.score == "a":
        fair.main(args.input, args.output, args.validate)
        # TODO: merge in these other outputs
        # care.main(args.input, args.output, args.validate)
        # lclabels.main(args.input, args.output, args.validate)
    else:
        raise ValueError("Unknown score input")
