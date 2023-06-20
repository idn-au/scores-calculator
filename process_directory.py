import os
import argparse
from pathlib import Path
from rdflib import Graph
from calculators.care import main as care_main
from calculators.fair import main as fair_main

def process_directory(directory: Path | str, validate: bool, skip_care: bool, skip_fair: bool):

    scores_path = Path(directory) / 'scores'
    scores_path.mkdir(parents=True, exist_ok=True)

    # List all files in the directory
    for file_path in Path(directory).glob("*.ttl"):
        # Create a full path to the file
        if not skip_care:
            care_output = str(scores_path / (file_path.stem + '-care.ttl'))
            care_main(file_path, care_output, validate)
        if not skip_fair:
            fair_output = str(scores_path / (file_path.stem + '-fair.ttl'))
            fair_main(file_path, fair_output, validate)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process a directory of RDF files.')
    parser.add_argument('-d', '--directory', type=str, required=True, help='The directory of RDF files to process.')
    parser.add_argument('-v', '--validate', action='store_true', help='Whether to validate the RDF files.')
    parser.add_argument('--skip-care', action='store_true', help='Whether to skip calculating a CARE score.')
    parser.add_argument('--skip-fair', action='store_true', help='Whether to skip calculating a FAIR score.')

    args = parser.parse_args()

    process_directory(args.directory, args.validate, args.skip_care, args.skip_fair)
