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
    if (window.Notification.permission != "denied") {
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

function urlBase64ToUint8Array(base64String) {
  const padding = "=".repeat((4 - (base64String.length % 4)) % 4);
  const base64 = (base64String + padding)
    .replace(/\-/g, "+")
    .replace(/_/g, "/");
  const rawData = window.atob(base64);
  return Uint8Array.from([...rawData].map((char) => char.charCodeAt(0)));
}

async function registerSubscription(reg) {
  const response = await fetch("/static/vapid_public.b64");
  const vapidPublicKey = await response.text();
  console.log(vapidPublicKey);
  reg.pushManager
    .subscribe({
      userVisibleOnly: true,
      applicationServerKey: urlBase64ToUint8Array(vapidPublicKey),
    })
    .then((sub) => {
      fetch("/subscribe", {
        method: "post",
        headers: {
          "Content-type": "application/json",
        },
        body: JSON.stringify({ subscription: sub }),
      });
      console.log("Endpoint:", sub.endpoint);
    })
    .catch((e) => {
      console.log("Could not subscribe to push:", e);
    });
}
