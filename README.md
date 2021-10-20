# sd-keeponeye

## About

`sd-keeponeye` aims at monitoring systemd services and notifying
failures. One goal of this tool is to bring back the nice functionality of
`cron`, which mails `stderr` output.

It features the following functionality:

* send mail upon job failure.

## Alternatives

The `OnFailure=` alternative consists in defining a unit called when
the monitored service fails. The drawback of this appproach is that this
needs to be done for each monitored service. Example implementation:

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
