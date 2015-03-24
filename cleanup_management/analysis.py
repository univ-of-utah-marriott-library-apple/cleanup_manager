import os


def get_date_based_deletable_inventory(keep_after, target=None, folders=None, files=None, links=None):
    """
    Finds all of the items within an inventory that can be deleted based on
    their last modification date.
    
    :param keep_after:
    :param target:
    :param folders:
    :param files:
    :param links:
    :return: lists of folers, files, and links to be deleted and/or unmade
    """
    if folders is None or files is None or links is None:
        if not target:
            raise ValueError("Must give either a target or the inventory.")
        else:
            folders, files, links = get_inventory(target)
    
    # Find the folders and files that need to be deleted.
    # If the item's score is above the threshold value, it will be deleted.
    # Folder and file lists are assumed to contain tuples as:
    #     (path, age, size)
    delete_folders = [folder[0] for folder in folders if folder[1] < keep_after]
    delete_files   = [file[0] for file in files if file[1] < keep_after]
    
    # Now handle links. This is a bit trickier.
    # Link array is assumed to contain tuples as:
    #     (link location, target location, inside)
    delete_links   = []
    for link in links:
        if link[2] and (link[1] in delete_folders or link[1] in delete_files):
            delete_links.append(link[0])
        else:
            for folder in delete_folders:
                if link[0].startswith(folder) or link[1].startswith(folder):
                    delete_links.append(link[0])
                    break
    
    # Return the deletable inventory.
    return delete_folders, delete_files, delete_links


def get_inventory(target):
    """
    Given a target directory, finds all subitems within that directory and
    stores them in separate lists, ie folders, files, and links.
    
    Folder and file lists are full of tuples as:
        (folder/file path, modification timestamp, size)
    where:
        folder/file path:       the patht to the object
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
    :return: a tuple containing lists containing tuples describing the contents
             as (folders, files, links)
    """
    if not os.path.isdir(target):
        raise ValueError("The target must be a valid, existing directory.")
    
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
            else:
                folders.append(folder)
        
        for file in subfiles:
            file = os.path.join(path, file)
            if os.path.islink(file):
                links.append(file)
            else:
                files.append(file)
        
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
                # If the modification time is more recent than that of the top
                # directory, overwrite the directory's age with the file's.
                file_age = os.path.getmtime(file)
                if file_age > age:
                    age = file_age
                # Is the file a link?
                if os.path.islink(file):
                    links.append(file)
                else:
                    size += os.path.getsize(file)
        
        folders[i] = (folder, age, size)
        
    ##--------------------------------------------------------------------------
    ## Get link information.
    ##--------------------------------------------------------------------------
    
    # Determine whether each link connects to a point within the top directory.
    links = [(link, os.path.realpath(link), os.path.realpath(link).startswith(target)) for link in links]
    
    return folders, files, links
