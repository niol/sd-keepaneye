% KEEPANEYE(8)
% Alexandre Rossi

# NAME

keepaneye - keeping an eye on systemd

# SYNOPSIS

**keepaneye** [**-h**] [**-d**] **SUBCOMMAND**

# DESCRIPTION

`sd-keepaneye` aims at monitoring systemd services and notifying
failures. One goal of this tool is to bring back the nice functionality of
`cron`, which mails `stderr` output.

It features the following functionality:

  * send mail upon job failure.

# OPTIONS

These programs follow the usual GNU command line syntax, with long
options starting with two dashes (\`-\'). A summary of options is
included below. For a complete description, see the `-h` switch.

`-d`

: Enable DEBUG level logging and log to STDOUT instead of journald.

`-h` `--help`

: Show summary of options.

# SUB-COMMANDS

`daemon`

: Start the daemon.

# CONFIGURATION FILE

The configuration file uses Tom's Obvious Minimal Language (TOML) as a
file format. An example configuration with all options is provided.

## SECTION KEEPANEYE

This section defines general configuration options.

`debug`

: same as `-d`, `true` or `false`

# FILES

`/lib/systemd/system/keepaneyed.service`

: SystemD service file.

`/etc/keepaneye.conf`

: Configuration file

# SEE ALSO

More information is available on the program website:
`https://sml.zincube.net/~niol/repositories.git/sd-keepaneye/about/`.

# AUTHOR

This manual page was written for the DEBIAN system (but may be used by
others). Permission is granted to copy, distribute and/or modify this
document under the terms of the GNU General Public License, Version 2
any later version published by the Free Software Foundation.

On Debian systems, the complete text of the GNU General Public License
can be found in /usr/share/common-licenses/GPL.
