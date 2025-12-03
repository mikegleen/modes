"""
    This module contains definitions that are specific to a particular implementation.
"""
DEFAULT_EXHIBITION_PLACE = 'HRM'
DEFAULT_EXHIBITION_LONG = 'Joan Brinsmead Gallery'
DEFAULT_MDA_CODE = 'LDHRM'  # must be upper case
DEFAULT_RECORD_TAG = 'Object'
DEFAULT_RECORD_ID_XPATH = './ObjectIdentity/Number'
#
# Set the number of zeros to pad digits with in accession numbers
#
DEFAULT_PREFIX_PADDING = {
    'JB': 3,
    'L': 3
}

# Set by Config.__init__ to avoid circular import
config_instance = None

