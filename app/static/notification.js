function handleNotificationWorker(workerScript) {
  if (navigator.serviceWorker) {
    navigator.serviceWorker.register(workerScript).then(
      (reg) => {
        reg.pushManager
          .getSubscription()
          .then((sub) => {
            if (sub == null) {
              console.log("Not subscribed to service");
            } else {
              console.log("Already subscribed:", sub);
            }
          })
          .catch((e) => {
            console.log("Could not get subscriptions:", e);
          });
      },
      (e) => {
        console.log("Could not register worker script:", e);
      }
    );
  } else {
    console.log("Browser doesn't support service workers");
  }
}

function subscribeUser() {
  if (window.Notification && navigator.serviceWorker) {
    if (window.Notification.permission == "default") {
      window.Notification.requestPermission().then((perm) => {
        if (perm == "granted") {
          navigator.serviceWorker.ready.then((reg) => {
            registerSubscription(reg);
          });
        }
      });
    }
  }
}

function registerSubscription(reg) {
  reg.pushManager
    .subscribe({ userVisibleOnly: true })
    .then((sub) => {
      console.log("Endpoint:", sub.endpoint);
    })
    .catch((e) => {
      console.log("Could not subscribe to push:", e);
    });
}
