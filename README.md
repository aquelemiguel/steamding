<p align=center>
  <img src="https://i.imgur.com/a6f46Lhr.png" width="600" /><br><br>
  Add a notification chime to your Steam achievements.
</p>

## Usage
1. Navigate to your Steam Community [**privacy settings**](https://steamcommunity.com/my/edit/settings) and ensure your **game details** are set to **public**.
2. **[Download](https://steamding.com), install and run the application.** You should now see a new icon on your application tray.
3. Right-click on the steamding icon and navigate to Options > Edit configuration... A configuration file should open. [Find your **steamid64**](https://steamid.io/) and paste it on the settings.ini file which opened. **Don't forget to save all changes.**
4. Press the **reload option** or restart the app.

## F.A.Q.
### How does steamding work?
You provide it your steamid64, your unique profile identifier. It then continuously web scrapes your Steam Community profile page, fetching the game you're currently playing and its achievement progress. Whenever that number changes, you get a notification. As simple as it needs to be.

### Why does my profile need to be public?
When you scrape a page, the bot can only see publicly available information, just like a human does. Therefore, if you hide which game you're playing on your Steam Community profile, the bot won't magically find it.

### Can this get me VAC banned?
Ah, the age old question. The app doesn't hook into any process so it's virtually impossible. Yet as I wouldn't trust random code on the internet either, the full source code is available on this repo. Your karambit is safe.

### It's busted!
It's inevitable, really. This is a side project of a overworked college student, so it's more than likely I've overlooked a few things. Hit me up at my email anytime and I'll gladly fix it ASAP.

### Is it free?
I couldn't charge you for a few lines of code. Reddit surprised me with its donations [last time](https://github.com/aquelemiguel/vreddit-mirror-bot) and I'm still overwhelmed with your support. 👏 [Link is always open if you'd like to cover hosting costs.](https://paypal.me/aquelemiguel)

## Troubleshooting
### "Could not find your profile!"
The application couldn't find your profile. Either you forgot to or incorrectly pasted your steamid64 on the config file.

### "Your profile appears to be private!"
Test whether your profile info can be seen when opened on an incognito window. If not, the game details subsection on your [privacy settings](https://steamcommunity.com/my/edit/settings) is likely set to private or friends only, when it should be public.

## Future improvements
* Using **Steam OpenID** login could fix the need to set the privacy settings to public although I'm not optimistic.

## Special thanks
Much love to [**Julieta**](https://github.com/julietafrade97) for designing the beautiful steamding logo, [**Conde**](https://github.com/joao-conde) for testing the code and [**Diogo**](https://github.com/diogodores) for putting together a web page for when at one point this was an Electron app.
