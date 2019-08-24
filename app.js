/* eslint-disable no-console */
require('dotenv').config({ path: 'variables.env' });

const express = require('express');
const path = require('path');

const app = express();
const http = require('http').createServer(app);

app.use(require('body-parser').json());

app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, '/views/index.html'));
});

app.get('/faq', (req, res) => {
  res.sendFile(path.join(__dirname, '/views/faq.html'));
});

app.use(express.static(path.join(__dirname, '/public')));
http.listen(process.env.PORT || 3000, () => console.log(`Listening on port ${process.env.PORT || 3000}.`));
