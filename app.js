const express = require('express');
const parser = require('body-parser');
const path = require('path');
const OpenIDStrategy = require('passport-openid').Strategy;
const session = require('express-session');
const passport = require('passport');

const app = express();
const port = 3000;

const scraper = require('./middlewares/scraper');

app.use(parser.urlencoded({ extended: true }));

const SteamStrategy = new OpenIDStrategy({
  providerURL: 'http://steamcommunity.com/openid',
  stateless: true,
  returnURL: `http://localhost:${port}/auth/openid/return`,
  realm: `http://localhost:${port}`,
}, (id, done) => process.nextTick(() => done(null, { identifier: id, steamID: id.match(/\d+$/)[0] })));

passport.use(SteamStrategy);
passport.serializeUser((user, done) => done(null, user.identifier));
passport.deserializeUser((id, done) => done(null, { identifier: id, steamID: id.match(/\d+$/)[0] }));

app.use(session({ secret: 'shh', resave: true, saveUninitialized: false }));
app.use(passport.initialize());
app.use(passport.session());

app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, '/views/index.html'));
});

app.get('/fetchprofile', (req, res) => {
  if (!req.user) res.sendStatus(200);
  else {
    scraper.fetchPlayerProfile('FE308435BF852EAD4175D2A70AA87C2D', req.user.steamID).then(
      profile => res.send(profile),
    ).catch(error => console.log(error));
  }
});

app.get('/auth/islogged', (req, res) => {
  res.send(req.user ? req.user.steamID : false);
});

app.get('/auth/openid/return', passport.authenticate('openid'), (req, res) => {
  if (req.user) res.redirect('/');
  else res.sendStatus(404);
});

app.post('/track', (req, res) => {
  req.achievements = -1;

  if (req.user) {
    scraper.fetchPlayerProfile('FE308435BF852EAD4175D2A70AA87C2D', req.user.steamID)
      .then(prof => setInterval(() => scraper.fetchAchievementNo(prof.profileurl, prof.gameid)
        .then((achievements) => {
          if (achievements > req.achievements) {
            req.achievements = achievements;
            console.log('change!');
          } else console.log(achievements);
        })
        .catch(error => console.log(error)), 5000))
      .catch(error => console.log(error));
  } else res.sendStatus(200);
});

app.get('/playerinfo', (req, res) => {
  scraper.fetchPlayerProfile('FE308435BF852EAD4175D2A70AA87C2D', req.user.steamID)
    .then(playerInfo => res.send(playerInfo))
    .catch(error => console.log(error));
});

app.post('/auth/openid', passport.authenticate('openid'));

app.post('/auth/logout', (req, res) => {
  req.logout();
  res.redirect('/');
});

app.use(express.static(path.join(__dirname, '/public')));
app.listen(port, () => console.log(`Listening on port ${port}.`));
