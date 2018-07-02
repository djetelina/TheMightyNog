# The Mighty Nog

Discord bot for Nognest discord server.

### Developing

* Get pipenv if you don't have it (`pip install pipenv` || `brew install pipenv`)
* Install all python dependencies: `pipenv install`
* Create `.env` file or export environmental variables (`NOG_BOT_TOKEN` and `NOG_DB_DSN` are required)
* Run: `pipenv run python src/main.py`

You can create a bot account [here](https://discordapp.com/developers/applications/me). The DB DSN is url for 
connecting to the database, used by `aiopg`/`psycopg2`. Format I'm using is: `postgres://user:password@host:port/db_name`