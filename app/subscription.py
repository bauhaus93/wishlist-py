import json
import time
from urllib.parse import urlparse

from pywebpush import WebPushException, webpush

from app import app, db, logger
from app.models import Subscription

log = logger.get()


def push_change_notification(title, message, change_timestamp):
    for sub in Subscription.query.all():
        if time.time() > sub.expires:
            db.session.delete(sub)
        elif sub.notification_timestamp < change_timestamp:
            try:
                sub_info = json.loads(sub.sub_json.replace("'", '"')).get(
                    "subscription", ""
                )
                aud = urlparse(sub_info.get("endpoint", ""))
                webpush(
                    subscription_info=sub_info,
                    data=message,
                    vapid_private_key=app.config.get("VAPID_PRIVATE"),
                    vapid_claims={
                        "sub": "mailto:schlemihl123@gmail.com",
                        "aud": f"{aud.scheme}://{aud.netloc}",
                        "exp": min(24 * 3600, sub.expires),
                    },
                )
                sub.notification_timestamp = change_timestamp
            except WebPushException as ex:
                log.error("Could not push notification: %s" % repr(ex))
    db.session.commit()
