const express = require('express');
const parser = require('body-parser');
const session = require('express-session');
const path = require('path');
const OpenIDStrategy = require('passport-openid').Strategy;
const passport = require('passport');
const soundController = require('./controllers/sound');

const app = express();
const port = 3000;

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

app.use(passport.initialize());
app.use(passport.session());

app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, '/views/index.html'));
});

app.get('/preview', (req, res) => {
  soundController.previewUnlockSound('xbox-360');
});

app.get('/auth/openid/return', passport.authenticate('openid'), (req, res) => {
  if (req.user) res.redirect(`/?steamid=${req.user.steamID}`);
  else res.redirect('/?failed');
});

app.post('/auth/openid', passport.authenticate('openid'));

app.post('/auth/logout', (req, res) => {
  req.logout();
  res.redirect('back');
});

app.use(express.static(path.join(__dirname, '/public')));
app.listen(port, () => console.log(`Listening on port ${port}.`));
