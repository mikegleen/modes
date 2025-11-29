from __future__ import annotations

DEFAULT_MDA_CODE = 'LDHRM'  # must be upper case
#
# Set the number of zeros to pad digits with in accession numbers
#
DEFAULT_PREFIX_PADDING = {
    'JB': 3,
    'L': 3
}

# Set by Config.__init__ to avoid circular import
config_instance = None

