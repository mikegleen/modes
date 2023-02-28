"""
    Convert the names of files to uppercase. Do not convert the file extension.

    One parameter is required, the directory holding the new images.

    The files in the directory are of the form: <accession #>.jpg
"""
import os.path
import sys

DRYRUN = False


def main():
    target_dir = sys.argv[1]
    files = os.listdir(target_dir)
    os.chdir(target_dir)

    n_updated = 0
    for filename in files:
        if filename.startswith('.'):
            continue
        if not filename.lower().endswith('.jpg'):
            print('Skipping non-jpg {}', filename)
            continue
        prefix, extension = os.path.splitext(filename)
        newfilename = prefix.upper() + extension.lower()
        if filename != newfilename:
            n_updated += 1
            if DRYRUN:
                print(f"Dry Run: {filename=} {newfilename=}")
            else:
                os.rename(filename, newfilename)
    return n_updated


if __name__ == '__main__':
    nupdated = main()
    print(f'{nupdated} file{"" if nupdated == 1 else "s"} updated.')
