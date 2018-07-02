#!/usr/bin/env bash
# Until I set up a proper CD, this is what I use to relaunch the bot
git pull
kill $(ps aux | grep '[b]in/python src/main.py' | awk '{print $2}')
pipenv sync
pipenv run python src/main.py &
disown
