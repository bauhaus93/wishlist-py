function handlePush(changeUrl) {
  var pushAsked = sessionStorage.getItem("pushAsked");
  if (pushAsked == null) {
    Push.create("Notifikationen aktiviert", {
      body: "",
      timeout: 4000,
      onClick: function () {
        window.focus();
        this.close();
      },
    });
    if (pushAsked == null) {
      sessionStorage.setItem("pushAsked", true);
    }
  }
  if (Push.Permission.has()) {
    registerPush(changeUrl);
  }
}

function registerPush(changeUrl) {
  var interval = setInterval(check_wishlist_changed, 2000, changeUrl);
}

function check_wishlist_changed(changeUrl) {
  $.get(changeUrl, function (response) {
    if (update_timestamp(response.lastChange) === true) {
      emitPush();
    }
  });
}

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

function emitPush() {
  Push.create("Neue Forderung!", {
    body: "Oweier",
    onClick: function () {
      window.focus();
      this.close();
    },
  });
}
