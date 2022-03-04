# sd-keepaneye

## About

`sd-keepaneye` aims at monitoring systemd services and notifying
failures. One initial goal of this tool was to bring back the nice
functionality of `cron`, which mails `stderr` output.

It features the following functionality:

* send mail upon systemd job completion: this feature is provided by
  `keepaneyed` which monitors systemd events using the D-Bus interface.
  It monitors all jobs and notifies when a job ends (only for failures in
  the default configuration).

## Alternatives

### `OnFailure=`

The `OnFailure=` alternative consists in defining a unit called when
the monitored service fails. Example implementation:

`/etc/systemd/system/unit-status-mail@.service`:

    [Unit]
    Description=Unit Status Mailer Service
    After=network.target

    [Service]
    Type=oneshot
    ExecStart=/usr/local/bin/unit-status-mail %I "Hostname: %H" "Machine ID: %m" "Boot ID: %b"

`/usr/local/bin/unit-status-mail`:

    #!/bin/bash

    MAILTO="root"
    MAILFROM="unit-status-mailer"
    UNIT=$1

    EXTRA=""
    for e in "${@:2}"; do
      EXTRA+="$e"$'\n'
    done

    UNITSTATUS=$(systemctl status $UNIT -l -n 9999)

    sendmail $MAILTO <<EOF
    From:$MAILFROM
    To:$MAILTO
    Subject:Status mail for unit: $UNIT

    Status report for unit: $UNIT
    $EXTRA

    $UNITSTATUS
    EOF

    echo -e "Status mail sent to: $MAILTO for unit: $UNIT"

and for instance `/etc/systemd/system/certbot.service.d/email-failure.conf`:

    [Unit]
    OnFailure=unit-status-mail@%n.service

Since [systemd v244](https://lists.freedesktop.org/archives/systemd-devel/2019-November/043772.html),
this can even be defined for all services:

> Unit files now support top level dropin directories of the form
> <unit_type>.d/ (e.g. service.d/) that may be used to add configuration
> that affects all corresponding unit files.

This is thus achieved in `/etc/systemd/system/service.d/email-failure.conf`:

    [Unit]
    OnFailure=unit-status-mail@%n.service

### systemd_mon

[`systemd_mon`](https://github.com/joonty/systemd_mon) does about the same
thing and can notify to slack or hipchat. However, the list of monitored
services must be specified in a configuration file.

### sagbescheid

[`sagbescheid`](https://github.com/mineo/sagbescheid) seems to do the same
and can notify to IRC. It also can monitor Unit state transitions.

## Contributing

### Code

Code may be downloaded using Git :

    $ git clone http://sml.zincube.net/~niol/repositories.git/sd-keepaneye

It is browsable online in
[sd-keepaneye's repository browser](http://sml.zincube.net/~niol/repositories.git/sd-keepaneye),
and this page also provides an up to date snapshot of the development
source tree.

Patches are very welcome.

## Bugs & feature requests

This project has too few users/contributors to justify the use of a dedicated
bug tracking application.

Bug reports and feature requests may go in :

* by e-mail, directly to <alexandre.rossi@gmail.com> (please put
  `sd-keepaneye` somewhere in the subject),
* through the [sd-keepaneye's Github bug tracker][2].

[2]: https://github.com/niol/sd-keepaneye/issues
