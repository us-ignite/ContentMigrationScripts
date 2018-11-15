from djangosite.wp_data_importer import run_imports
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("import_file", help="Include the file to parse.")
    args = parser.parse_args()
    run_imports(args.import_file)