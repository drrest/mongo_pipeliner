import argparse

parser = argparse.ArgumentParser(description='Migration utility for MongoDB')
parser.add_argument('-l', '--list',
                    dest="show_migrations",
                    default=False,
                    help='Show list of ap[lied migrations',
                    required=False,
                    action="store_true")

arguments = parser.parse_args()
