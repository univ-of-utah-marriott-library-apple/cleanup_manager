Cleanup Manager
===============

Cleanup Manager helps you clean up folders on your Mac's hard drive.

## Contents

* [Contact](#contact) - how to reach us
* [System Requirements](#system-requirements) - what you need
* [Download](#download) - get it here!
* [Purpose](#purpose) - why it does what it does
* [Usage](#usage) - how to make Cleanup Manager do the thing
* [Details](#details) - how the things are done
* [Update History](#update-history) - history of the project

## Contact

If you have any comments, questions, or other input, either [file an issue](../../issues) or [send us an email](mailto:mlib-its-mac-github@lists.utah.edu). Thanks!

## System Requirements

* Mac OS X
  * Tested on 10.9 and 10.10
* Python 2.7.x (which comes preinstalled on OS X, or you can download a non-Apple version [here](https://www.python.org/download/))
* [Management Tools](https://github.com/univ-of-utah-marriott-library-apple/management_tools) - version 1.8.1 or greater

## Download

[Download the latest installer for Cleanup Manager here!](../../releases/)

## Purpose

Cleanup Manager was originally designed to help cleanup user home folders on shared, frequently-used machines. We use it in some student labs that have persistent login information where the users' home folders can accumulate and aren't deleted for long periods of time. Cleanup Manager is also used to manage shared drives that have a tendency to fill up quickly.

## Usage

```
$ cleanup_manager.py [-hvnV] [-l log] [-k date] [-f format] target
```

### Options

| Option                                | Purpose                                                                       |
|---------------------------------------|-------------------------------------------------------------------------------|
| `-h`, `--help`                        | Print help message and quit.                                                  |
| `-v`, `--version`                     | Print version information and quit.                                           |
| `-n`, `--no-log`                      | Redirect logging to standard output.                                          |
| `-V`, `--verbose`                     | Increase verbosity of output (can be used twice).                             |
| `--skip-prompt`                       | Skips the confirmation prompt. Be careful with this.                          |
| `-l log`, `--log-dest log`            | Change the destination log file of log events.                                |
| `-k date`, `--keep-after date`        | The date to keep items after. Default is seven days prior to invocation.      |
| `-d format`, `--date-format format`   | Format of the given date. Useful if you have that one particular way of formatting your dates and you don't want to change. |
| `-f size`, `--freeup size`            | The amount of space to attempt to free up.                                    |
| `--delete-oldest-first`               | When deleting by size, older items are deleted first. This is the default.    |
| `--delete-largest-first`              | When deleting by size, larger items are deleted first.                        |
| `--overflow`                          | Allows the script to delete more than just the size specified to hit target.  |

`target` is a path to a directory that you want to clean up.

### Examples

To delete *up to* 15 gigabytes of data within the target directory, while deleting the oldest items first:

```
$ cleanup_manager.py -f 15g /path/to/target
```

To attempt to reach 500 megabytes free on the drive with preference given to larger items:

```
$ cleanup_manager.py -f 500mf --delete-largest-first /path/to/target
```

To clear up 30% of the drive where `target` exists by deleting items inside of `target` (witth preference given to older items):

```
$ cleanup_manager.py -f 30 /path/to/target
```

## Details

After being given a directory to examine, the Cleanup Manager navigates the entire directory tree. Files in the top level are recorded with their last modification timestamp, and folders are navigated to find the most recent item within them. Anything that, from the top level (`target`), has a most-recent modification timestamp that is older than the `--keep-after` date will be deleted.

Links are examined to see whether they either:

1. exist inside of a folder that will be deleted, or
2. point to something else that will be deleted.

Any link that meets either of these criteria will be unmade.

## Update History

This is a short, reverse-chronological summary of the updates to this project.

| Date       | Version   | Update Description                                                           |
|------------|:---------:|------------------------------------------------------------------------------|
| 2015-05-19 | 1.3.0     | New `--overflow` flag ensures specified disk space will be cleared.          |
| 2015-05-18 | 1.2.0     | Added increased verbosity availability via more `-V` flags.                  |
| 2015-03-31 | 1.1.1     | Amended logic to handle combinations of size- and date-based deletions.      |
| 2015-03-27 | 1.1.0     | Proper release with size-based deleting of things.                           |
| 2015-03-27 | 1.1.0pre4 | Script actually handles size-based options properly. Updated in-line docs.   |
| 2015-03-27 | 1.1.0pre3 | Implemented logic for deleting inventory items based on size.                |
| 2015-03-26 | 1.1.0pre2 | Completed the handling of user instructions for size-based deletion.         |
| 2015-03-24 | 1.1.0pre1 | Working to add size-based deletion (instead of just date-based).             |
| 2015-02-27 | 1.0.0     | Actual first release. Fairly stable and usable.                              |
| 2015-02-26 | 1.0.0a    | Moved the module directory to a different name than the script.              |
| 2015-02-26 | 1.0.0rc3  | Now asks for confirmation prior to deleting things.                          |
| 2015-02-26 | 1.0.0rc2  | Apparently changing the value of '__name__' is a bad idea.                   |
| 2015-02-26 | 1.0.0rc1  | Uncommented lines that cause deletion. First trials in-action.               |
| 2015-02-26 | 0.9.3     | Docstrings added to all methods.                                             |
| 2015-02-26 | 0.9.2     | Added in-script documentation and help feature.                              |
| 2015-02-26 | 0.9.1     | Updated `main` method and init.                                              |
| 2015-02-26 | 0.9.0     | Most of the functionality put in place for analysis and deletion.            |
| 2014-10-03 | 0.1       | Project started.                                                             |
