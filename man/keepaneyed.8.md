% KEEPANEYED(8)
% Alexandre Rossi

# NAME

keepaneyed - keeping an eye on systemd

# SYNOPSIS

**keepaneyed** **-h** | **-d**

# DESCRIPTION

`sd-keeponeye` aims at monitoring systemd services and notifying
failures. One goal of this tool is to bring back the nice functionality of
`cron`, which mails `stderr` output.

It features the following functionality:

  * send mail upon job failure.

# OPTIONS

These programs follow the usual GNU command line syntax, with long
options starting with two dashes (\`-\'). A summary of options is
included below. For a complete description, see the `-h` switch.

`-d`

: Enable DEBUG level loggging and log to STDOUT instead of journald.

`-h` `--help`

: Show summary of options.

# FILES

`/lib/systemd/system/keepaneyed.service`

: SystemD service file.

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
