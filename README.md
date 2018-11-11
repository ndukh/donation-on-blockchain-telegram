# TelegramTracker
###  The module shows the direct functionality of the product.
[Telegram-bot](https://t.me/MasterchainCharityBot) client which allows to check by a donation ID how the donation was spent.

It uses the [donation-on-blockhain-api](https://github.com/AplusD/dontation-on-blockchain-api)

It is almost ready for deploying on IBM Bluemix CF (Python buildpack). Before deployment it is essential to:
- amend the parameters of `config_example.ini`;
- rename `config_example.ini` to `config.ini`;
- rename app in `manifest.yml`;
- *probably* make some other changes in [`manifest.yml`](https://docs.cloudfoundry.org/devguide/deploy-apps/manifest.html).
