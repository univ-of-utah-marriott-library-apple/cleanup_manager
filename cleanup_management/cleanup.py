import os
import shutil
import sys


def delete_links(links, logger):
    """
    Unmake all of the links.
    
    :param links: A list containing paths to link objects to be deleted.
    :param logger: A Management Tools Logger object for handling output.
    """
    for link in links:
        try:
            logger.info("    Unlinking: {}".format(link))
            os.unlink(link)
        except IOError as (errno, strerror):
            logger.error("I/O Error({}): {}".format(errno, strerror))
        except:
            logger.error("{}: {}".format(sys.exc_info()[0].__name__, sys.exc_info()[1]))


def delete_files(files, logger):
    """
    Remove all of the files.
    
    :param files: A list containing paths to files to be deleted.
    :param logger: A Management Tools Logger object for handling output.
    """
    for file in files:
        try:
            logger.info("    Deleting File: {}".format(file))
            os.remove(file)
        except IOError as (errno, strerror):
            logger.error("I/O Error({}): {}".format(errno, strerror))
        except:
            logger.error("{}: {}".format(sys.exc_info()[0].__name__, sys.exc_info()[1]))


def delete_folders(folders, logger):
    """
    Recursively delete the folders.
    
    :param folders: A list containing folders to be deleted.
    :param logger: A Management Tools Logger object for handling output.
    """
    for folder in folders:
        try:
            logger.info("    Removing Directory: {}".format(folder))
            shutil.rmtree(folder)
        except IOError as (errno, strerror):
            logger.error("I/O Error({}): {}".format(errno, strerror))
        except:
            logger.error("{}: {}".format(sys.exc_info()[0].__name__, sys.exc_info()[1]))
