from datetime import date
from django.conf import settings
from example_app.models import FedWireInfo
from importer import *
from string import capwords

import os


class Command( HTTPLoader, LineReader, ParsingImporter):

    help  = "Load the FedWire directory into the database."
    
    # The original URL for the directory is:
    # https://www.frbservices.org/EPaymentsDirectory/fpddir.txt
    # As of Dec 9th, 2018 the Complete E-Payments Routing Directory file
    # will be / was removed from the FRB site, so we use an (outdated)
    # Github copy to demonstrate custom parsing.

    url   = 'https://raw.githubusercontent.com/chrisortman/AchLookup/master/fpddir.txt'
    model = FedWireInfo
    open_mode = 'r'

    def parse( self, s):
        t = s[93:101].strip()
        lastrev = date( int( t[:4]), int( t[4:6]), int( t[6:])) if t else None
        return self.model(
            bank_code  = int( s[:9]),
            telex_name = s[9:27].strip(),
            bank_name  = s[27:63].strip(),
            state      = s[63:65],
            city       = capwords( s[65:90].strip()),
            modified   = lastrev,
            funds_transfer_elegible = s[90] == 'Y',
            funds_settlement_only   = s[91] == 'S',
            bes_transfer_elegible   = s[92] == 'Y')
