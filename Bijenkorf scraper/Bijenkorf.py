import requests
import pandas as pd
# import numpy as np
# import time
from utils import headers, queries
import tabulate
# import sys

startindex=0

def query_article(productCode, productVariantCode, productReferer):
  headers['referer'] = productReferer

  params = (
    ('productCode', productCode),
    ('productVariantCode', productVariantCode),
    ('cached', 'false'),
    ('locale', 'nl_NL'),
    ('api-version', '2.36'),
  )

  response = requests.get('https://ceres-catalog.debijenkorf.nl/catalog/product/show', headers=headers, params=params)
  return response.json()

df = pd.DataFrame()

for targetgroup in ['Men', 'Women', 'Boys', 'Girls']:
  index, artnr = 0, 0

  # Keep quering next productlists until you receive an empty list.
  while(True):
    # Replace the indexvariable in the query string
    query = queries[targetgroup].replace('**INDEXPLACEHOLDER**', f'fh_start_index={index}')

    # Pass the query to the server
    response = requests.post('https://www.debijenkorf.nl/api/graphql', headers=headers, data=query)

    # Transform response in json and get variables of interest
    data = response.json()
    productList = data['data']['productListing']['navigation']['products']
    totalItemCount = data['data']['productListing']['navigation']['pagination']['totalItemCount']

    # Let the server think you are accesing the article from the 'current' page
    referer = 'https://www.debijenkorf.nl/' + data['data']['productListing']['navigation']['pagination']['currentPage']['relativeUrl']

    # Check if the productlist has products, else break the while loop
    if len(productList) == 0:
      break

    # Create dictionary that will hold all the variables of interest for each article SKU
    articleSKU = {}

    print(f'Current query index: {index}')
    # Iterate over general article info in queried productlist
    for data in productList:
      artnr+=1

      articleSKU['brand'] = data['brand']['name']
      articleSKU['code'] = data['code']
      articleSKU['name'] = data['name']

      print(f'Article {artnr}/{totalItemCount}: {data["name"]}')

      # Query detailed data for current article
      articleQuery = query_article(articleSKU['code'], data['currentVariantProduct']['code'], referer)

      articleSKU['category01'] = targetgroup
      
      # Category 2 untill 4 may sometimes be missing
      for i in range(2,5):
        try:
          articleSKU[f'category0{i}'] = articleQuery['data']['product']['categoryPath'][i]['name']
        except (IndexError, TypeError):
          articleSKU[f'category0{i}'] = None

      # Obtain data on a SKU level
      for data in articleQuery['data']['product']['variantProducts']:
        articleSKU['OSP'] = data['sellingPrice']['value']

        try:
          articleSKU['ASP'] = data['overriddenPrices'][0]['value']
        except IndexError:
          articleSKU['ASP'] = articleSKU['OSP']

        # Default = low quality, web_detail = high_quality
        articleSKU['URL'] = data['selectionImage']['url'].replace('default', 'web_detail')

        articleSKU['Size'] = data['size']
        articleSKU['Color'] = data['color']
        articleSKU['Stock'] = data['availability']['stock']

        # Append the SKU article to the final Dataframe
        df = df.append(articleSKU, ignore_index=True)
        if artnr == 2:
          print(df.to_markdown())
          #exit()

    # Get next 240 articles (=max stepsize)
    index = index + 240

