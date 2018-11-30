stamp rally with line-bot and google 360 media

* line bot
* google 360 app

# installation guide
1. python 

* pipenv

```
pipenv install;pipenv shell
python3 main.py

```

2. nginx
* encrypt with certbot

```
cp -r ./proxy/nginx/ /etc/nginx/

# install certbot
# https://certbot.eff.org
sudo certbot --nginx
```
