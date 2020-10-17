function requestPush() {
  if (window.Notification) {
    console.log(window.Notification.permission);
    if (window.Notification.permission == "granted") {
      emitNotification("Aktiv", "Notifications sind aktiviert!");
    } else if (window.Notification.permission == "default") {
      window.Notification.requestPermission().then(function (perm) {
        if (perm == "granted") {
          emitNotification("Aktiv", "Notifications wurden aktiviert!");
        }
      });
    }
  } else {
    console.log("Browser doesn't support notifications");
  }
}

function registerPush(changeUrl) {}

function check_wishlist_changed(changeUrl) {}

function update_timestamp(lastChange) {
  var lastChangeLocal = sessionStorage.getItem("lastChange");
  if (lastChangeLocal == null) {
    sessionStorage.setItem("lastChange", lastChange);
    return true;
  } else if (lastChangeLocal < lastChange) {
    sessionStorage.setItem("lastChange", lastChange);
    return true;
  }
  return true;
}

function emitNotification(title, body) {
  var options = {
    body: body,
    silent: true,
  };
  new Notification(title, options);
}
