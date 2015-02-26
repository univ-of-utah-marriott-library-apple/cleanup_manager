import os
import shutil
import sys


def delete_links(links):
    """
    
    :param links:
    :param logger:
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
    
    :param files:
    :param logger:
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
    
    :param folders:
    :param logger:
    """
    for folder in folders:
        try:
            shutil.rmtree(folder)
        except IOError as (errno, strerror):
            logger.error("I/O Error({}): {}".format(errno, strerror))
        except:
            logger.error("{}: {}".format(sys.exc_info()[0].__name__, sys.exc_info()[1]))
