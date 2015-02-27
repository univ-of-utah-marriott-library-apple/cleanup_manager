import os
import shutil
import sys


def delete_links(links):
    """
    Unmake all of the links.
    
    :param links: A list containing paths to link objects to be deleted.
    """
    for link in links:
        try:
            os.unlink(link)
        except IOError as (errno, strerror):
            logger.error("I/O Error({}): {}".format(errno, strerror))
        except:
            logger.error("{}: {}".format(sys.exc_info()[0].__name__, sys.exc_info()[1]))


def delete_files(files):
    """
    Remove all of the files.
    
    :param files: A list containing paths to files to be deleted.
    """
    for file in files:
        try:
            os.remove(file)
        except IOError as (errno, strerror):
            logger.error("I/O Error({}): {}".format(errno, strerror))
        except:
            logger.error("{}: {}".format(sys.exc_info()[0].__name__, sys.exc_info()[1]))


def delete_folders(folders):
    """
    Recursively delete the folders.
    
    :param folders: A list containing folders to be deleted.
    """
    for folder in folders:
        try:
            shutil.rmtree(folder)
        except IOError as (errno, strerror):
            logger.error("I/O Error({}): {}".format(errno, strerror))
        except:
            logger.error("{}: {}".format(sys.exc_info()[0].__name__, sys.exc_info()[1]))
