import colorama
import os


def search_in_all_subdirs(top_directory, filename=None,
                          infilename=None,
                          filestarting="", fileending="",
                          expected=None, **kwargs):
    # find all files in the directory and in its subdirectories that
    # matches the pattern.
    # start by listing the path of all files
    files = get_all_subfiles(top_directory, **kwargs)
    to_return = []
    for f in files:
        name = os.path.basename(f)
        if filename is not None:
            if name == filename:
                to_return.append(f)
            # don't consider other criterion
            continue
        if infilename is not None:
            if infilename in name:
                to_return.append(f)
            # don't consider other criterion
            continue
        if name.startswith(filestarting) and name.endswith(fileending):
            to_return.append(f)
    if expected is not None:
        # check if number of files found matches what was expected
        if expected != len(to_return):
            raise ValueError("Found more or less files as expected.")
    return to_return


def get_all_subfiles(top_directory, ignore=None):
    # return a list of the path of all files and subfiles in this dir.
    # ignore removes undesired subdirectories
    entries = list(os.listdir(top_directory))
    if isinstance(ignore, str):
        ignore = [ignore, ]
    if ignore is not None:
        for ign in ignore:
            if ign in entries:
                entries.remove(ign)
    files_here = [os.path.join(top_directory, x)
                  for x in entries
                  if os.path.isfile(os.path.join(top_directory, x))]
    files = files_here
    for subdir in [os.path.join(top_directory, x)
                   for x in entries
                   if os.path.isdir(os.path.join(top_directory, x))]:
        files += get_all_subfiles(subdir)
    return files


def styled_text(text, color="", style=""):
    return style + color + text + colorama.Style.RESET_ALL
