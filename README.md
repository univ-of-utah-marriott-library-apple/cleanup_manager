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

## Contact

If you have any comments, questions, or other input, either [file an issue](../../issues) or [send us an email](mailto:mlib-its-mac-github@lists.utah.edu). Thanks!

## System Requirements

* Mac OS X
  * Tested on 10.9 and 10.10
* Python 2.7.x (which comes preinstalled on OS X, or you can download a non-Apple version [here](https://www.python.org/download/))
* [Management Tools](https://github.com/univ-of-utah-marriott-library-apple/management_tools) - version 1.7.0 or greater

## Download

[Download the latest installer for Cleanup Manager here!](../../releases/)

## Purpose

Cleanup Manager was originally designed to help cleanup user home folders on shared, frequently-used machines. We use it in some student labs that have persistent login information where the users' home folders can accumulate and aren't deleted for long periods of time. Cleanup Manager is also used to manage shared drives that have a tendency to fill up quickly.

## Usage

```
$ cleanup_manager.py [-hvnV] [-l log] [-k date] [-f format] target
```

### Options

| Option                         | Purpose                                                                  |
|--------------------------------|--------------------------------------------------------------------------|
| `-h`, `--help`                 | Print help message and quit.                                             |
| `-v`, `--version`              | Print version information and quit.                                      |
| `-n`, `--no-log`               | Redirect logging to standard output.                                     |
| `-V`, `--verbose`              | Increase verbosity of output (can be used twice).                        |
| `-l log`, `--log-dest log`     | Change the destination log file of log events.                           |
| `-k date`, `--keep-after date` | The date to keep items after. Default is seven days prior to invocation. |
| `-f format`, `--format format` | Format of the given date. Useful if you have that one particular way of formatting your dates and you don't want to change. |

`target` is a path to a directory that you want to clean up.

## Details

After being given a directory to examine, the Cleanup Manager navigates the entire directory tree. Files in the top level are recorded with their last modification timestamp, and folders are navigated to find the most recent item within them. Anything that, from the top level (`target`), has a most-recent modification timestamp that is older than the `--keep-after` date will be deleted.

Links are examined to see whether they either:

1. exist inside of a folder that will be deleted, or
2. point to something else that will be deleted.

Any link that meets either of these criteria will be unmade.
