import sqlalchemy as sa

metadata = sa.MetaData()

servers = sa.Table(
    'servers', metadata,
    sa.Column('name', sa.String(256), primary_key=True),
    sa.Column('address', sa.String(256), nullable=False),
    sa.Column('cbsapi', sa.String(256)),
    sa.Column('owner', sa.BigInteger, sa.ForeignKey('users.id_'))
)


users = sa.Table(
    'users', metadata,
    sa.Column('id_', sa.BigInteger, primary_key=True),  # discord id
    sa.Column('granted_permission', sa.TIMESTAMP)  # GDPR, in case any of this is considered personal
)


user_server_nicknames = sa.Table(
    'user_server_nicknames', metadata,
    sa.Column('server_name', sa.String(256), sa.ForeignKey('servers.name'), primary_key=True),
    sa.Column('user_id', sa.BigInteger, sa.ForeignKey('users.id_')),
    sa.Column('user_nickname', sa.String(256), primary_key=True),
)
