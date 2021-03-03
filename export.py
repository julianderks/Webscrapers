import pandas as pd
import sqlalchemy
from six.moves import urllib
import math

def to_DWH(table):
    df = pd.read_pickle(table + '.pkl')

    server = '...'
    database = '...'
    password = '...'

    params = urllib.parse.quote_plus("DRIVER={SQL Server};SERVER=%s;DATABASE=%s;UID=%s;PWD=%s" % (server, database, table, password))
    engine = sqlalchemy.create_engine("mssql+pyodbc:///?odbc_connect=%s" % params)
    cnxn = engine.connect()

    # Append to table in Datawarehouse
    df.to_sql(name=table, con=engine, index=False, if_exists='append', chunksize=math.floor(2100/13), method='multi')
    print("Data saved to DWH!")