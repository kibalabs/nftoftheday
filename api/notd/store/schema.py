import sqlalchemy

metadata = sqlalchemy.MetaData()

TokenTransfersTable = sqlalchemy.Table(
    'tbl_token_transfers',
    metadata,
    sqlalchemy.Column(name='id', type_=sqlalchemy.Integer, autoincrement=True, primary_key=True, nullable=False),
    sqlalchemy.Column(name='transaction_hash', type_=sqlalchemy.Text, nullable=False),
    sqlalchemy.Column(name='registry_address', type_=sqlalchemy.Text, nullable=False),
    sqlalchemy.Column(name='from_address', type_=sqlalchemy.Text, nullable=False),
    sqlalchemy.Column(name='to_address', type_=sqlalchemy.Text, nullable=False),
    sqlalchemy.Column(name='token_id', type_=sqlalchemy.Text, nullable=False),
    sqlalchemy.Column(name='value', type_=sqlalchemy.Numeric(precision=256, scale=0), nullable=False),
    sqlalchemy.Column(name='gas_limit', type_=sqlalchemy.Numeric(precision=256, scale=0), nullable=False),
    sqlalchemy.Column(name='gas_price', type_=sqlalchemy.Numeric(precision=256, scale=0), nullable=False),
    sqlalchemy.Column(name='gas_used', type_=sqlalchemy.Numeric(precision=256, scale=0), nullable=False),
    sqlalchemy.Column(name='block_number', type_=sqlalchemy.Integer, nullable=False),
    sqlalchemy.Column(name='block_hash', type_=sqlalchemy.Text, nullable=False),
    sqlalchemy.Column(name='block_date', type_=sqlalchemy.DateTime, nullable=False),
)
