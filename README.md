# Rival Sports / Performance Plus Physio WhatsApp Bot

A menu-driven WhatsApp bot. It answers questions about services, the two centres (with Google Maps links), timings, conditions treated, and service area. It sends emergency contact info. For bookings, it sends the Google registration form (https://forms.gle/1ZQy8KrBSV5LBSKR9) with the payment steps, and when a patient sends an image or file (the payment screenshot), it thanks them and says the team will confirm. Registrations are collected in the Google Form's responses.

To change any business details or reply text, edit `business_info.py`.

## 1. Try it locally (no WhatsApp needed)

```
pip install -r requirements.txt
python bot.py
```

## 2. Connect it to WhatsApp (Meta WhatsApp Cloud API)

1. Go to https://developers.facebook.com and create an app of type **Business**, then add the **WhatsApp** product.
2. Under **WhatsApp > API Setup**, copy the **access token** and the **Phone number ID**. Add your own phone as a test recipient.
3. Copy `.env.example` to `.env` and fill in those values.
4. Run the server with `python main.py`. It listens on port 5000.
5. Make the server reachable from the internet:
   - For testing: `ngrok http 5000`, then use the `https://…ngrok…` URL.
   - For production: host it at `https://bot.rivalsports.in` (see section 4).
6. Under **WhatsApp > Configuration > Webhook**, set:
   - Callback URL: `https://YOUR-URL/webhook`
   - Verify token: the same `WHATSAPP_VERIFY_TOKEN` as in `.env`
   - Then subscribe to the **messages** field.
7. Send "hi" to the test number from WhatsApp.

## 3. Go live on the real number with coexistence (keep using the WhatsApp Business App)

Coexistence lets +91 9804218167 stay active in the WhatsApp Business App while the bot answers through the API. It has to be set up through a Meta partner. These steps use 360dialog.

1. Update the WhatsApp Business App on the phone to the latest version.
2. Sign up at 360dialog and connect the number with their coexistence / "WhatsApp Business App" onboarding. Scan the code shown in the app when asked.
3. Create an API key in the 360dialog hub. In `.env`, set `WHATSAPP_PROVIDER=360dialog` and `D360_API_KEY=...`.
4. Host the bot at `https://bot.rivalsports.in` (see section 4).
5. Point 360dialog at it: `python main.py set-webhook https://bot.rivalsports.in/webhook`
6. Make sure "message echoes" (`smb_message_echoes`) events are enabled, so the bot knows when you reply from the app.

When you or your staff reply to a customer from the Business App, the bot goes quiet with that customer for `BOT_PAUSE_HOURS` (default 4). The customer can type *menu* to bring the bot back. Other customers aren't affected.

Things that change with coexistence: broadcast lists become read-only, linked devices are logged out (WhatsApp for Windows isn't supported), groups don't sync, and messages the bot sends are billed at Cloud API rates. Messages you send from the app stay free.

## 4. Host it at bot.rivalsports.in (Render)

`render.yaml` sets everything up: an always-on server in Singapore and the `bot.rivalsports.in` domain. It starts on Render's free plan, which sleeps after 15 minutes without messages, so the first reply after a quiet spell can take up to a minute. Once real patients use the bot, switch the bot service to the Starter plan (about $7/month, always awake) under **Settings > Instance Type**.

1. Put this folder in a **private** GitHub repository. `.gitignore` keeps `.env` out of it.
2. On https://render.com, click **New > Blueprint** and pick the repository.
3. Fill in the secret values when asked (`WHATSAPP_TOKEN`, `WHATSAPP_PHONE_NUMBER_ID`, `WHATSAPP_VERIFY_TOKEN` or `D360_API_KEY`).
4. Where you bought rivalsports.in, open the DNS settings and add:
   - Type `CNAME`, name/host `bot`, value `rival-sports-whatsapp-bot.onrender.com` (use the exact address Render shows under **Settings > Custom Domains**).
5. Wait for Render to show the domain as verified (HTTPS is set up automatically). Then `https://bot.rivalsports.in` should say "bot is running".
6. Use `https://bot.rivalsports.in/webhook` as the webhook URL, and `https://bot.rivalsports.in/privacy` as the privacy policy URL in the Meta app settings.

Registrations arrive in the Google Form's **Responses** tab. To get an email for each new registration, open the form, go to **Responses**, click the three dots, and choose **Get email notifications for new responses**.

### The website (rivalsports.in)

The same blueprint also publishes the `website/` folder as a free static site at `rivalsports.in` and `www.rivalsports.in`. In your domain's DNS settings, add the records Render shows under the website's **Settings > Custom Domains**. Usually that's:
- Type `A`, name `@`, value `216.24.57.1`
- Type `CNAME`, name `www`, value `rival-sports-website.onrender.com`

Use the exact values Render shows. To change the site, edit `website/index.html` and push to GitHub. Render redeploys it automatically.

## Notes
- Paused chats are kept in memory, so restarting the server un-pauses everyone.
- The bot only replies once it's running AND the number is connected to the WhatsApp API (section 3). Until then, messages to +91 9804218167 go only to the WhatsApp Business App, and no bot replies.
