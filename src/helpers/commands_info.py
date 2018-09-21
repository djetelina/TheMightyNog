"""
This could eventually just read all the descriptions from toml file or something. Right now let's be lazy like this

Used to generate !help when passed to @command.command
"""
main = """
I am The Mighty Nog! I'll help you around here"""
users_register = dict(
    description="Register with a bot\n"
                "TheMightyNog will remember your discord id and will be able to associate "
                "useful information with that.",
    brief="Register with the bot"
)
users_consent = dict(
    description="Give consent to the bot storing your potentionally personal information",
    brief="Give consent with personal information storage after registering",
    usage="yes"
)
servers_servers = dict(
    description="Lists all available servers",
    brief="Lists all available servers"
)
servers_publish = dict(
    name='publish',
    description="Publishes a server for people to browse. \n"
                "Please provide the name of the server and it's address (with port)",
    brief='Publishes a server for people to browse',
    usage="<server_name> <server_address>"
)

servers_delete = dict(
    name='delete',
    description='Deletes a server from the database.',
    brief='Deletes a server from the database',
    usage="<server_name>"
)

servers_cbsapi = dict(
    name='cbsapi',
    description="Changes whether you are running cbsapi alongside your server\n"
                "To enable provide a value that points to your API address"
                "To disable try: `no`, `off`, `disabled`, `disable`\n"
                "You can get cbsapi at: https://github.com/kbasten/CBSAPI",
    brief='Changes whether you are running cbsapi alongside your server',
    usage="<server_name> <state_value>"
)
servers_rating = dict(
    description="Gets rating of a user, WIP"
)

servers_top = dict(
    description="Gets top 10 of a server",
    brief="Gets top 10 of a server"
)
servers_player = dict(
    description="Gets game server information about a player",
    brief="Gets game server information about a player"
)

generic_patreon = dict(
    description="URL of ScrollsGuide patreon page",
    brief='URL of ScrollsGuide patreon page'
)
