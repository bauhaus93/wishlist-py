self.addEventListener("push", (evt) => {
  var options = {
    body: "WOHOO",
    silent: true,
  };
  evt.waitUntil(self.registration.showNotification("UPDATE", options));
});
