"""
    Remove files to be deferred from a batch directory and move them to a defer
    directory.

    Input is the directory containing the batch to split (like batch001) and
    a CSV file whose first field contains the accession number of the image
    to keep (that is, not defer).

    If a file is not named in the CSV file it is moved from the input batch to
    a defer batch named like batch001-defer.

    Make sure the batch files are backed up before running this.

"""

