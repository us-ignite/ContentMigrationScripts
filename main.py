from PixelpillowMigration.wp_data_importer import run_imports
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("import_file", help="Include the file to parse.")
    parser.add_argument("username", help="WP username to use for api connection")
    parser.add_argument("pw", help="WP user password to use for api connection")
    args = parser.parse_args()
    run_imports(args.import_file, args.username, args.pw)