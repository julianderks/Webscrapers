import pandas as pd
import sqlalchemy
from six.moves import urllib
import math

# df = pd.read_csv("BijenkorfData.csv", sep=';', index_col=0)
params = urllib.parse.quote_plus("DRIVER={SQL Server};SERVER=cat-SQL01.cat-Dom.local;DATABASE=CI_interfaces;UID=Scraper_Bijenkorf;PWD=5cr@p3r")
engine = sqlalchemy.create_engine("mssql+pyodbc:///?odbc_connect=%s" % params)
cnxn = engine.connect()

# Read table
sql = "SELECT * FROM Scraper_Bijenkorf"
df = pd.read_sql(sql, cnxn)

print(df)

# print(df.dtypes)
# # Write table
# df.to_sql(name='Scraper_bijenkorf', con=engine, index=False, if_exists='append',
#           chunksize=math.floor(2100/13), method='multi')

