import time

import config


def build_recipients(policy, extra=[]):
    extra.append(policy["holder_email"])
    extra.append(config.ADJUSTER_EMAIL)
    return extra


def send_notification(policy, message):
    recipients = build_recipients(policy)
    for r in recipients:
        time.sleep(0.2)  # simulate SMTP round trip
        print(f"[NOTIFY] to={r} msg={message}")
    return recipients
