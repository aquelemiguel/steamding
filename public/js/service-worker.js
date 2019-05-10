/* eslint-disable no-restricted-globals */
self.addEventListener('push', (event) => {
  const data = event.data.json();
  self.registration.showNotification(data.title, { body: 'it worked!' });
});
