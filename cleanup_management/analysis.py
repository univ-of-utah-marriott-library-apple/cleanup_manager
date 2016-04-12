import os


def get_date_based_deletable_inventory(keep_after, logger, target=None, folders=None, files=None, links=None, trigger=None):
    """
    Finds all of the items within an inventory that can be deleted based on
    their last modification date.

    :param keep_after: a unix timestamp; any files or directories with a last
                       modification time after this will be removed
    :param logger: a Management Tools logger object
    :param target: the directory to clean out
    :param folders: an inventory of the folders (see get_inventory())
    :param files: an inventory of the files (see get_inventory())
    :param links: an inventory of the links (see get_inventory())
    :return: lists of folers, files, and links to be deleted and/or unmade
    """
    if folders is None or files is None or links is None:
        if not target:
            raise ValueError("Must give either a target or the inventory.")
        else:
            folders, files, links = get_inventory(target, logger)
    else:
        # Make copies of the inventory lists just in case the user wanted to
        # keep the originals.
        folders = list(folders)
        files   = list(files)
        links   = list(links)

    logger.verbose("Getting date-based deletable inventory:")

    # Check if any of the folders contain the trigger file.
    # If they do, and if that trigger file's last modified timestamp is within
    # the specified range, set that folder to be removed.
    delete_folders = []
    if trigger is not None:
        pop_indices = []
        # Iterate over the folders with their index in the list.
        for index, folder in enumerate(folders):
            triggerpath = os.path.join(folder[0], trigger)
            # Test if the trigger file exists in the folder.
            try:
                if os.path.getmtime(triggerpath) < keep_after:
                    # If the file exists and its timestamp is old enough, then
                    # the folder should be deleted.
                    pop_indices.append(index)
            except OSError:
                # The file does not exist in the folder. That's fine; we'll just
                # continue on and let it be deleted naturally if it ought to be.
                continue
        # Go through the marked indices and add the appropriate folders to the
        # deletion list.
        for index in pop_indices:
            delete_folders.append(folders[index])
        # Then go through and remove those folders from the original list.
        for index in pop_indices:
            folders.pop(index)
        # Note that these steps must be separated. If the folders were popped at
        # the same time they're added to the delete_folders list, the indices
        # would change and you would be adding the wrong folders.

    # Find the folders and files that need to be deleted.
    # If the item's score is above the threshold value, it will be deleted.
    # Folder and file lists are assumed to contain tuples as:
    #     (path, age, size)
    # Effectively, for each folder/file: if that item has a timestamp that is
    # less than the 'keep_after' value, it gets added to the list.
    delete_folders += [folder[0] for folder in folders if folder[1] < keep_after]
    delete_files    = [file[0] for file in files if file[1] < keep_after]

    # Now handle links. This is a bit trickier.
    # Link array is assumed to contain tuples as:
    #     (link location, target location, inside)
    delete_links   = []
    for link in links:
        # If the link points inside the 'target' directory and the target of the
        # link will be deleted during cleanup, then remove the link.
        if link[2] and (link[1] in delete_folders or link[1] in delete_files):
            delete_links.append(link[0])
        else:
            for folder in delete_folders:
                # If the link exists inside of or points into a folder that is
                # going to be deleted, then remove the link.
                if link[0].startswith(folder) or link[1].startswith(folder):
                    delete_links.append(link[0])
                    break

    # Print out lots of fun information if it's warranted.
    for folder in delete_folders:
        logger.debug("    Set to remove folder: {}".format(folder))
    for file in delete_files:
        logger.debug("    Set to remove file: {}".format(file))
    for link in delete_links:
        logger.debug("    Set to remove link: {}".format(link))

    # Return the deletable inventory.
    return delete_folders, delete_files, delete_links


def get_size_based_deletable_inventory(target_space, logger, target=None, oldest_first=True, overflow=False, folders=None, files=None, links=None):
    """
    Finds all of the items within an inventory that can be deleted based on a
    given target amount of space to attempt to free up.

    :param target_space: the amount of space to attempt to clean up
    :param logger: a Management Tools logger object
    :type  target_space: int
    :param target: the directory to clean out
    :param oldest_first: whether to prefer deleting old itmes first; if set to
                         False, then largest items will be deleted first
    :param folders: an inventory of the folders (see get_inventory())
    :param files: an inventory of the files (see get_inventory())
    :param links: an inventory of the links (see get_inventory())
    :return: list of folders, files, and links to be deleted and/or unmade and
             the total amount of stuff deleted (in bytes)
    """
    if folders is None or files is None or links is None:
        if not target:
            raise ValueError("Must give either a target or the inventory.")
        else:
            folders, files, links = get_inventory(target, logger)
    else:
        # Make copies of the inventory lists just in case the user wanted to
        # keep the originals.
        folders = list(folders)
        files   = list(files)
        links   = list(links)

    logger.verbose("Getting size-based deletable inventory:")

    # Initialize lists to be returned.
    delete_folders = []
    delete_files   = []
    delete_links   = []

    # # Set the index key based on oldest/largest preference.
    # if oldest_first:
    #     key = 1
    # else:
    #     key = 2
    # Initialize an accumulated_size counter to keep track of how much stuff is
    # going to be deleted.
    accumulated_size = 0

    # Build up the deletion lists.
    while accumulated_size < target_space:
        logger.verbose("  target_space     = {}".format(target_space))
        logger.verbose("  accumulated_size = {}".format(accumulated_size))
        # If we have folders left but no files, just look at the maximum value
        # for the folders.
        if folders and not files:
            if oldest_first:
                folder = min(folders, key=lambda folder: folder[1])
            else:
                folder = max(folders, key=lambda folder: folder[2])
            logger.verbose("    folder: {}".format(folder))
            logger.verbose("      age: {}".format(folder[2]))
            # If that folder's size won't put us over the 'total_size' alotment,
            # add it to the list of folders to be deleted.
            if overflow or folder[2] <= target_space - accumulated_size:
                delete_folders.append(folder[0])
                accumulated_size += folder[2]
                logger.verbose("      deleting")
            # In any case, remove the folder from the list of folders.
            # This way we can keep iterating over the list and not get stuck on
            # one value.
            folders.remove(folder)

        # Files but no folders.
        elif files and not folders:
            if oldest_first:
                file = min(files, key=lambda file: file[1])
            else:
                file = max(files, key=lambda file: file[2])
            logger.verbose("    file: {}".format(file))
            logger.verbose("      age: {}".format(file[2]))
            # If the file's size won't put us over the 'total_size' alotment,
            # add it do the list of files to be deleted.
            if overflow or file[2] <= target_space - accumulated_size:
                delete_files.append(file[0])
                accumulated_size += file[2]
                logger.verbose("      deleting")
            # Even if the file is too big to be deleted, remove it from the list
            # of files so we don't have to see it again.
            files.remove(file)

        # Maybe we have both! That's kind of tricky.
        elif files and folders:
            # Take the maximum value from each of 'folders' and 'files'.
            if oldest_first:
                folder = min(folders, key=lambda folder: folder[1])
                file   = min(files, key=lambda file: file[1])
            else:
                folder = max(folders, key=lambda folder: folder[2])
                file   = max(files, key=lambda file: file[2])
            logger.verbose("    folder: {}".format(folder))
            logger.verbose("      age: {}".format(folder[2]))
            logger.verbose("    v file: {}".format(file))
            logger.verbose("      age: {}".format(file[2]))
            # If the folder is older/larger than the file...
            if (oldest_first and folder[1] <= file[1]) or (not oldest_first and folder[2] >= file[2]):
                logger.verbose("    folder preferred")
                # Add the folder to the list of folders to be deleted.
                if overflow or folder[2] <= target_space - accumulated_size:
                    delete_folders.append(folder[0])
                    accumulated_size += folder[2]
                    logger.verbose("      deleting folder")
                # Remove the folder from the list of folders.
                folders.remove(folder)
            # But if the file is older/larger...
            else:
                logger.verbose("    file preferred")
                # Add the file to the list of files to be deleted.
                if overflow or file[2] <= target_space - accumulated_size:
                    delete_files.append(file[0])
                    accumulated_size += file[2]
                    logger.verbose("      deleting file")
                # Remove the file from the list of files.
                files.remove(file)

        # We don't have any folders or files left, so quit the loop.
        # If this gets triggered, it means that there weren't enough items in
        # the target directory to fill up the 'total_size' alotment.
        else:
            break

    # Now handle links. This is a bit trickier.
    # Link array is assumed to contain tuples as:
    #     (link location, target location, inside)
    for link in links:
        # If the link points inside the 'target' directory and the target of the
        # link will be deleted during cleanup, then remove the link.
        if link[2] and (link[1] in delete_folders or link[1] in delete_files):
            delete_links.append(link[0])
        else:
            for folder in delete_folders:
                # If the link exists inside of or points into a folder that is
                # going to be deleted, then remove the link.
                if link[0].startswith(folder) or link[1].startswith(folder):
                    delete_links.append(link[0])
                    break

    # Print out lots of fun information if it's warranted.
    for folder in delete_folders:
        logger.debug("    Set to remove folder: {}".format(folder))
    for file in delete_files:
        logger.debug("    Set to remove file: {}".format(file))
    for link in delete_links:
        logger.debug("    Set to remove link: {}".format(link))

    # Return the deletable inventory and accumulated size.
    return delete_folders, delete_files, delete_links, accumulated_size


def get_inventory(target, logger):
    """
    Given a target directory, finds all subitems within that directory and
    stores them in separate lists, ie folders, files, and links.

    Folder and file lists are full of tuples as:
        (folder/file path, modification timestamp, size)
    where:
        folder/file path:       the path to the object
        modification timestamp: the Unix timestamp of the last modification
        size:                   the size of the object
    Folder sizes are just the sum of their content, and folder modification
    times are considered to be the most-recent timestamp among all objects
    within that folder.

    Link list is full of tuples as:
        (link path, target path, internal)
    where:
        link path:   the path to the link object
        target path: the target that the link points to
        internal:    whether the target is in this inventory

    :param target: directory to search for inventory
    :param logger: a Management Tools logger object
    :return: a tuple containing lists containing tuples describing the contents
             as (folders, files, links)
    """
    if not os.path.isdir(target):
        raise ValueError("The target must be a valid, existing directory.")

    logger.verbose("Getting top-level inventory:")

    ##--------------------------------------------------------------------------
    ## Get top-level directory listings.
    ##--------------------------------------------------------------------------

    # Initialize lists to hold tuples.
    folders = []
    files   = []
    links   = []

    # Walk through everything in just the top directory.
    for path, subdirs, subfiles in os.walk(target):
        for folder in subdirs:
            folder = os.path.join(path, folder)
            if os.path.islink(folder):
                links.append(folder)
                logger.verbose("    Found link: {}".format(folder))
            else:
                folders.append(folder)
                logger.verbose("    Found folder: {}".format(folder))

        for file in subfiles:
            file = os.path.join(path, file)
            if os.path.islink(file):
                links.append(file)
                logger.verbose("    Found link: {}".format(file))
            else:
                files.append(file)
                logger.verbose("    Found file: {}".format(file))

        # Prevent recursion to reduce time (we don't need everything indexed).
        break

    ##--------------------------------------------------------------------------
    ## Get file information.
    ##--------------------------------------------------------------------------

    # Get the age and size of each file.
    files = [(file, os.path.getmtime(file), os.path.getsize(file)) for file in files]

    ##--------------------------------------------------------------------------
    ## Get folder information.
    ##--------------------------------------------------------------------------

    # Get the age of each folder.
    for i in range(len(folders)):
        folder = folders[i]
        age    = os.path.getmtime(folder)
        size   = 0

        for path, subdirs, subfiles in os.walk(folder):
            for directory in subdirs:
                directory = os.path.join(path, directory)
                # If the modification time is more recent than that of the top
                # directory, overwrite the directory's age with the file's.
                directory_age = os.path.getmtime(directory)
                if directory_age > age:
                    age = directory_age
                # Is the directory a link?
                if os.path.islink(directory):
                    links.append(directory)

            for file in subfiles:
                file = os.path.join(path, file)
                file_age = 0
                # Is the file a link?
                if os.path.islink(file):
                    links.append(file)
                else:
                    size += os.path.getsize(file)
                    file_age = os.path.getmtime(file)
                # If the modification time is more recent than that of the top
                # directory, overwrite the directory's age with the file's.
                if file_age > age:
                    age = file_age

        folders[i] = (folder, age, size)

    ##--------------------------------------------------------------------------
    ## Get link information.
    ##--------------------------------------------------------------------------

    # Determine whether each link connects to a point within the top directory.
    links = [(link, os.path.realpath(link), os.path.realpath(link).startswith(target)) for link in links]

    return folders, files, links
