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


def main(target, keep_after, logger):
    """
    """
    target = os.path.abspath(target)
    
    folders, files, links = cleanup_manager.analysis.get_inventory(target)
    
    delete_folders, delete_files, delete_links = cleanup_manager.analysis.get_deletable_inventory(keep_after=keep_after, folders=folders, files=files, links=links)
    
    logger.info("Deleting contents recursively older than {} from {}".format(datetime.datetime.fromtimestamp(keep_after), target))
    
    # Remove links first.
    logger.info("Removing bad links:")
    if len(delete_links) == 0:
        logger.debug("    [NONE]")
    else:
        for link in delete_links:
            logger.verbose("    {}".format(link))
        # cleanup_manager.cleanup.delete_links(delete_links, logger)
        logger.debug("Bad links removed.")
    
    # Then delete files.
    logger.info("Removing files:")
    if len(delete_files) == 0:
        logger.debug("    [NONE]")
    else:
        for file in delete_files:
            logger.verbose("    {}".format(file))
        # cleanup_manager.cleanup.delete_files(delete_files, logger)
        logger.debug("Files removed.")
    
    # And then delete folders.
    logger.info("Removing folders:")
    if len(delete_folders) == 0:
        logger.debug("    [NONE]")
    else:
        for folder in delete_folders:
            logger.verbose("    {}".format(folder))
        # cleanup_manager.cleanup.delete_folders(delete_folders, logger)
        logger.debug("Folders removed.")
    
    logger.info("Cleanup complete.")


def version():
    """
    """
    return ("")


def usage():
    """
    """
    print("")


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

if __name__ == '__main__':
    # Build the argument parser.
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('-h', '--help', action='store_true')
    parser.add_argument('-v', '--version', action='store_true')
    parser.add_argument('-n', '--no-log', action='store_true')
    parser.add_argument('-V', '--verbose', action='count')
    parser.add_argument('-l', '--log-dest')
    parser.add_argument('-k', '--keep-after', default='-7d')
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
    
    # Set the logging level.
    if args.verbose is None:
        log_level = 20
    elif args.verbose == 1:
        log_level = 10
    else:
        log_level = 5
    
    # Build the logger.
    logger = loggers.get_logger(
        name  = "",
        log   = not args.no_log,
        level = log_level,
        path  = args.log_dest
    )
    
    # Set output logging prompts.
    for logging_level in [x for x in logger.prompts.keys() if x <= loggers.INFO]:
        logger.set_prompt(logging_level, '')
    
    # Get the Unix timestamp of the deletion date.
    keep_after = date_to_unix(args.keep_after, args.format)
    
    main(args.target, keep_after, logger)
