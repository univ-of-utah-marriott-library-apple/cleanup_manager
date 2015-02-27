#!/usr/bin/env python

import cleanup_manager

import argparse
import datetime
import os
import sys
import time


try:
    from management_tools import loggers
except ImportError as e:
    print("You need version 1.7.0 or greater of the 'Management Tools' module to be installed first.")
    print("https://github.com/univ-of-utah-marriott-library-apple/management_tools")
    raise e


def main(target, keep_after, skip_prompt, logger):
    target = os.path.abspath(target)
    
    folders, files, links = cleanup_manager.analysis.get_inventory(target)
    
    delete_folders, delete_files, delete_links = cleanup_manager.analysis.get_deletable_inventory(keep_after=keep_after, folders=folders, files=files, links=links)
    
    if not skip_prompt:
        logger.info("These items will be deleted:")
        
        if len(delete_links) > 0:
            logger.info("    Links:")
            for link in delete_links:
                logger.info("        {}".format(link))
        
        if len(delete_files) > 0:
            logger.info("    Files:")
            for file in delete_files:
                logger.info("        {}".format(file))
        
        if len(delete_folders) > 0:
            logger.info("    Folders:")
            for folder in delete_folders:
                logger.info("        {}".format(folder))
        
        if not query_yes_no("Proceed with cleanup?"):
            sys.exit(7)
    
    logger.info("Deleting contents recursively older than {} from {}".format(datetime.datetime.fromtimestamp(keep_after), target))
    
    # Remove links first.
    logger.info("Removing bad links:")
    if len(delete_links) == 0:
        logger.debug("    [NONE]")
    else:
        for link in delete_links:
            logger.verbose("    {}".format(link))
        # cleanup_manager.cleanup.delete_links(delete_links)
        logger.debug("Bad links removed.")
    
    # Then delete files.
    logger.info("Removing files:")
    if len(delete_files) == 0:
        logger.debug("    [NONE]")
    else:
        for file in delete_files:
            logger.verbose("    {}".format(file))
        # cleanup_manager.cleanup.delete_files(delete_files)
        logger.debug("Files removed.")
    
    # And then delete folders.
    logger.info("Removing folders:")
    if len(delete_folders) == 0:
        logger.debug("    [NONE]")
    else:
        for folder in delete_folders:
            logger.verbose("    {}".format(folder))
        # cleanup_manager.cleanup.delete_folders(delete_folders)
        logger.debug("Folders removed.")
    
    logger.info("Cleanup complete.")

def query_yes_no(question):
    """
    Asks a user a yes/no question and expects a valid response.
    
    :param question: The prompt to give to the user.
    :return: A boolean; True for 'yes', False for 'no'.
    """
    valid = {
        'yes': True, 'ye': True, 'y': True,
        'no': False, 'n': False
    }
    
    # Until they give valid input, loop and keep asking the question.
    while True:
        # Note the comma at the end. We don't want a newline.
        print("{} [y/N] ".format(question)),
        choice = raw_input().lower()
        if choice == '':
            return False
        elif choice in valid:
            return valid[choice]
        else:
            print("Please respond with 'yes' or 'no'.")


def version():
    """
    :return: The version information for this program.
    """
    return ("{name}, version {version}\n".format(name='cleanup_manager', version=cleanup_manager.__version__))


def usage():
    """
    Prints usage information.
    """
    print(version())
    
    print('''\
usage: {name} [-hvnV] [-l log] [-k date] [-f format] target

Delete old items from a specific directory, but only at a top-level granularity.

    -h, --help
        Print this help message and quit.
    -v, --version
        Print the version information and quit.
    -n, --no-log
        Do not output log events to file.
    -V, --verbose
        Increase verbosity to see more information. Two levels of verbosity are
        supported.
    --skip-prompt
        Skips the confirmation prompt. Warning: this will lead to lots of
        deletion.

    -l log, --log-dest log
        Redirect log file output to 'log'.
    -k date, --keep-after date
        The date to compare file modification times to. Anything before this
        date will be removed.
        default: seven days prior to today, rounded down to midnight
    -f format, --format format
        The date format, given as a Python datetime.datetime.strptime()-
        compatible format.
        default: '%Y-%m-%d'
    
    target
        The top-level directory to delete from within.

Cleanup Manager is a simple script to help you delete items from folders en
masse.

Originally conceived to delete user home directories in student labs at a
university, Cleanup Manager takes a look at a directory's contents and checks
them recursively for the most recently-modified timestamp. This timestamp is
compared against the keep-after date, and any item with a timestamp older than
that date is deleted.

KEEP-AFTER DATE
    The date can be either absolute or relative. Absolute dates can be given
    with a format to indicate how you want it parsed.

    Relative dates can be given as:
        NNNXr
    where "N" is an integer number, "X" represents a shorthand form of
    the time scale, i.e.:
        M - minutes
        H - hours
        d - days
        m - months
        y - years
    and "r" or "R" indicates that the date should be rounded back to
    the previous midnight.
    
EXAMPLE
    To delete everything older than four days ago:
        cleanup_manager.py -k 4d

LINKS
    All links existing within the directory structure are checked for whether
    they point internally; that is, if a link points to a file or folder that is
    going to be deleted, or if it is in a folder that is going to be deleted,
    the link is unmade. However, this program does not check the rest of the
    system to ensure that external links do not point inside a deleted
    directory.\
'''.format(name='cleanup_manager'))


def date_to_unix(date, date_format):
    """
    Converts a date to a local Unix timestamp (non-UTC).
    
    The date can be either absolute or relative. Absolute dates can be given
    with a format to indicate how you want it parsed.
    
    Relative dates can be given as:
        NNNXr
    where "N" is an integer number, "X" represents a shorthand form of
    the time scale, i.e.:
        M - minutes
        H - hours
        d - days
        m - months
        y - years
    and "r" or "R" indicates that the date should be rounded back to
    the previous midnight.
    
    :param date:
    :param date_format:
    :return: The Unix timestamp of the given date as a float.
    """
    try:
        # Attempt to pull the time out directly based on the format.
        target_date = datetime.datetime.strptime(date, date_format)
    except ValueError:
        # If that didn't work, let's try to parse the string for a relative
        # date according to the given specifications.
        import re
        relative_match = re.match(r"\A-?(\d+)([a-zA-Z]?)([rR]?)\Z", date)
        
        if relative_match:
            # If no scale is given, "D" is assumed.
            if not relative_match.group(2):
                scale = 'd'
            else:
                scale = relative_match.group(2)
            
            # If rounding is not specified, don't do it.
            if not relative_match.group(3):
                rounding = False
            else:
                rounding = True
            
            # Set the amount of change.
            amount = int(relative_match.group(1))
            
            if scale == 'M':
                # Minutes
                seconds = amount * 60
            elif scale == 'H':
                # Hours
                seconds = amount * 60 * 60
            elif scale == 'd':
                # Days
                seconds = amount * 60 * 60 * 24
            elif scale == 'm':
                # Months
                seconds = amount * 60 * 60 * 24 * 30
            elif scale == 'y':
                # Years
                seconds = amount * 60 * 60 * 24 * 365
            else:
                # Invalid specification.
                raise ValueError("{date} is not a valid relative date value".format(date=date))
            
            days    = seconds / 86399
            seconds = seconds % 86399
            
            time_difference = datetime.timedelta(days=days, seconds=seconds)
            
            # Calculate the target date.
            target_date = datetime.datetime.now() - time_difference
            
            # If rounding was specified, round to the previous midnight.
            if rounding:
                target_date = target_date.replace(hour=0, minute=0, second=0, microsecond=0)
        else:
            # Neither of these is valid. Raise an exception.
            raise ValueError("{date} is not a valid date specification".format(date=date))
    
    # Buidl up the current time for Unix time conversion.
    time_tuple = time.struct_time((
        target_date.year, target_date.month, target_date.day,
        target_date.hour, target_date.minute, target_date.second, -1, -1, -1
    ))
    unix_time = time.mktime(time_tuple) + (target_date.microsecond / 1e6)
    
    return unix_time

##------------------------------------------------------------------------------
## Program entry point.
##------------------------------------------------------------------------------

if __name__ == '__main__':
    # Build the argument parser.
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('-h', '--help', action='store_true')
    parser.add_argument('-v', '--version', action='store_true')
    parser.add_argument('-n', '--no-log', action='store_true')
    parser.add_argument('-V', '--verbose', action='count')
    parser.add_argument('--skip-prompt', action='store_true')
    parser.add_argument('-l', '--log-dest')
    parser.add_argument('-k', '--keep-after', default='-7dr')
    parser.add_argument('-f', '--format', default='%Y-%m-%d')
    parser.add_argument('target', nargs='?', default=os.getcwd())
    
    # Parse the arguments.
    args = parser.parse_args()
    
    if args.help:
        usage()
        sys.exit(0)
    
    if args.version:
        print(version())
        sys.exit(0)
    
    # Set the logging level. There's the regular level, the verbose level,
    # and the super-verbose level.
    if args.verbose is None:
        log_level = 20
    elif args.verbose == 1:
        log_level = 10
    else:
        log_level = 5
    
    # Build the logger.
    logger = loggers.get_logger(
        name  = 'cleanup_manager',
        log   = not args.no_log,
        level = log_level,
        path  = args.log_dest
    )
    
    # Set output logging prompts.
    for logging_level in [x for x in logger.prompts.keys() if x <= loggers.INFO]:
        logger.set_prompt(logging_level, '')
    
    # Get the Unix timestamp of the deletion date.
    keep_after = date_to_unix(args.keep_after, args.format)
    
    # Run it!
    try:
        main(
            target     = args.target,
            keep_after = keep_after,
            skip_prompt = args.skip_prompt,
            logger     = logger,
        )
    except:
        # Output the exception with the error name and its message. Suppresses the stack trace.
        logger.error("{errname}: {error}".format(errname=sys.exc_info()[0].__name__, error=sys.exc_info()[1].message))
        sys.exit(3)
