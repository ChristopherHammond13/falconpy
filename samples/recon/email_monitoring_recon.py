r"""Add monitoring rules for email addresses provided in a csv file (1 email address per row)

 _____     _                  __  __  ____
|  ___|_ _| | ___ ___  _ __   \ \/ / |  _ \ ___  ___ ___  _ __
| |_ / _` | |/ __/ _ \| '_ \   \  /  | |_) / _ \/ __/ _ \| '_ \
|  _| (_| | | (_| (_) | | | |  /  \  |  _ <  __/ (_| (_) | | | |
|_|  \__,_|_|\___\___/|_| |_| /_/\_\ |_| \_\___|\___\___/|_| |_|

Creation: 06.21.2022, wozboz@CrowdStrike
"""
from csv import reader
from argparse import ArgumentParser, RawTextHelpFormatter
from falconpy import Recon


parser = ArgumentParser(description=__doc__, formatter_class=RawTextHelpFormatter)
req = parser.add_argument_group("required arguments")
req.add_argument("-k", "--falcon_client_id",
                 help="CrowdStrike Falcon API Client ID",
                 required=True
                 )
req.add_argument("-s", "--falcon_client_secret",
                 help="CrowdStrike Falcon API Client Secret",
                 required=True
                 )
parser.add_argument("-b", "--base_url",
                    help="CrowdStrike base URL (only required for GovCloud, pass usgov1)",
                    required=False,
                    default="auto"
                    )

parser.add_argument("-f", "--file",
                    help="File with email-addresses to use as input",
                    required=True,
                    )

args = parser.parse_args()


EMAIL_FILE = args.file

falcon = Recon(client_id=args.falcon_client_id,
               client_secret=args.falcon_client_secret,
               base_url=args.base_url
               )

QUERY = "("
with open(EMAIL_FILE, encoding="utf-8") as read_file:
    csv_reader = reader(read_file)
    NUM_FOUND = 0
    for row in csv_reader:
        NUM_FOUND += 1
        QUERY += "email:'" + str(row[0]) + "',"
        if NUM_FOUND % 20 == 0:
            QUERY = QUERY[:-1]
            QUERY += ")"
            response = falcon.create_rules(filter=f"{QUERY}",
                                           name=f"Functional Email Addresses{int(NUM_FOUND/20)}",
                                           priority="medium",
                                           topic="SA_EMAIL",
                                           permissions="public",
                                           )
            QUERY = "("

QUERY = QUERY[:-1]
QUERY += ")"
response = falcon.create_rules(filter=f"{QUERY}",
                               name=f"Functional Email Addresses{NUM_FOUND}",
                               priority="medium",
                               topic="SA_EMAIL",
                               permissions="public",
                               )

print(f"Successfully created monitoring rules for {NUM_FOUND} email addresses.")
