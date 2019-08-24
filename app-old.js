/* eslint-disable no-console */
require('dotenv').config({ path: 'variables.env' });

const express = require('express');
const path = require('path');
const OpenIDStrategy = require('passport-openid').Strategy;
const session = require('express-session');
const passport = require('passport');

const app = express();
const http = require('http').createServer(app);
const io = require('socket.io')(http);

const scraper = require('./middlewares/scraper');

app.use(require('body-parser').json());

// Socket.io handling.
const clients = {};

io.on('connection', (socket) => {
  socket.on('ADD_CLIENT', (id) => {
    clients[id] = socket.id;
    console.log(`User ${id} registered to socket ${socket.id}!`);
    io.to(clients[id]).emit('LOG', 'Registered.');
  });
});

const log = (req, msg) => {
  io.to(clients[req.user.steamID]).emit('LOG', msg);
  console.log(msg);
};

// Steam login handling.
const SteamStrategy = new OpenIDStrategy({
  providerURL: 'http://steamcommunity.com/openid',
  stateless: true,
  returnURL: `http://localhost:${process.env.port}/auth/openid/return`,
  realm: `http://localhost:${process.env.port}`,
}, (id, done) => process.nextTick(() => done(null, { identifier: id, steamID: id.match(/\d+$/)[0] })));

passport.use(SteamStrategy);
passport.serializeUser((user, done) => done(null, user.identifier));
passport.deserializeUser((id, done) => done(null, { identifier: id, steamID: id.match(/\d+$/)[0] }));

app.use(session({ secret: 'shh', resave: true, saveUninitialized: false }));
app.use(passport.initialize());
app.use(passport.session());

// Renderer Steam account verifications.
app.get('/auth/islogged', (req, res) => {
  res.send(req.user ? req.user.steamID : false);
});

app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, '/views/index.html'));
});

app.get('/faq', (req, res) => {
  res.sendFile(path.join(__dirname, '/views/faq.html'));
});

app.get('/logged', (req, res) => {
  res.sendFile(path.join(__dirname, '/views/logged.html'));
});

app.get('/fetchprofile', (req, res) => {
  if (!req.user) res.sendStatus(200);
  else {
    scraper.fetchPlayerProfile('FE308435BF852EAD4175D2A70AA87C2D', req.user.steamID).then(
      profile => res.send(profile),
    ).catch(error => log(req, error.message));
  }
});

app.get('/auth/openid/return', passport.authenticate('openid'), (req, res) => {
  if (req.user) res.redirect('/logged');
  else res.sendStatus(404);
});

app.post('/track', (req, res) => {
  req.achievements = -1;
  req.currAppID = -1;
  req.hasAlreadyTriggered = false;

  setInterval(() => scraper.fetchPlayerProfile(process.env.API_KEY, req.user.steamID)
    .then((profile) => {
      if (profile) { req.profileObj = profile; clearInterval(this); }
    }).catch(err => log(req, err)), process.env.POLLING_RATE_PROFILE || 5000);

  setInterval(() => scraper.scrapeCurrentGame(req.profileObj).then((game) => {
    if (game && game !== 'Online' && game.match(/^Last Online/) === null) {
      scraper.getAppIDByGameName(game).then((appid) => {
        //  This means the player has stopped playing the current game and
        //  entered other, therefore, the achievement count should be reset.
        if (appid === -1 || appid !== req.currAppID) {
          req.currAppID = appid;
          req.achievements = -1;
        } else req.currAppID = appid;
      }).catch(err => log(req, err.message));
    }
  }).catch(err => log(req, err.message)), process.env.POLLING_RATE_GAME || 1000);

  setInterval(() => scraper.fetchAchievementNo(req.profileObj, req.currAppID).then((count) => {
    //  Hopefully disallow triggering the achievement twice.
    if (req.hasAlreadyTriggered) {
      req.hasAlreadyTriggered = false;
    }
    //  The 2nd condition should only be triggered when manually editing achievements with SAM.
    if ((count && req.achievements === -1) || count < req.achievements) {
      req.achievements = count;
    }
    if (count && count > req.achievements && !req.hasAlreadyTriggered) {
      io.to(clients[req.user.steamID]).emit('ACHIEVEMENT_UNLOCKED');
      req.hasAlreadyTriggered = true;
      req.achievements = count;
    }
  }).catch(err => log(req, err.message)), process.env.POLLING_RATE_ACHIEVEMENTS || 200);
});

app.get('/playerinfo', (req, res) => {
  scraper.fetchPlayerProfile(process.env.API_KEY, req.user.steamID)
    .then(playerInfo => res.send(playerInfo))
    .catch(err => log(req, err.message));
});

app.post('/auth/openid', passport.authenticate('openid'));

app.post('/auth/logout', (req, res) => {
  req.logout();
  res.redirect('/');
});

app.use(express.static(path.join(__dirname, '/public')));
http.listen(process.env.PORT || 3000, () => console.log(`Listening on port ${process.env.PORT || 3000}.`));
