headers = {
    'authority': 'www.debijenkorf.nl',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.135 Safari/537.36',
    'content-type': 'application/graphql',
    'accept': '*/*',
    'origin': 'https://www.debijenkorf.nl',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-mode': 'cors',
    'sec-fetch-dest': 'empty',
    'referer': 'https://www.google.nl',
    'accept-language': 'en-US,en;q=0.9',
    }

baseQuery = "query { productListing(query: \"\"\"fh_location=//catalog01/nl_NL/**CATEGORYPLACEHOLDER**&fh_view_size=240&**INDEXPLACEHOLDER**&country=NL&chl=1&vt=unknown\"\"\", locale: \"nl-NL\") { \n    navigation {\n        products {\n            \n    brand {\n        \n    name\n\n    }\n    code\n    colorCount\n    currentVariantProduct {\n        \n    availability {\n        \n    available\n    availableFuture\n    stock\n\n    }\n    code\n    color\n    current\n    images {\n        \n    position\n    type\n    url\n\n    }\n    overriddenPrices {\n        \n    currencyCode\n    type\n    value\n\n    }\n    sellingPrice {\n        \n    currencyCode\n    type\n    value\n\n    }\n    signings {\n        \n    discount {\n        \n    key\n    text\n\n    }\n    merchandise {\n        \n    key\n    text\n\n    }\n\n    }\n    trackingMetadata\n    size\n    url\n\n    }\n    defaultVariantCode\n    description\n    designer\n    displayName\n    displayProperties {\n        \n    currentVariantSelected\n    detailPageVariation\n\n    }\n    gift\n    name\n    subBrand {\n        \n    name\n\n    }\n    supplierModel\n    sustainable\n    trackingMetadata\n    url\n    variantProducts (limit:4, groupBy: COLOR) {\n        \n    availability {\n        \n    available\n    availableFuture\n    stock\n\n    }\n    code\n    color\n    current\n    images {\n        \n    position\n    type\n    url\n\n    }\n    overriddenPrices {\n        \n    currencyCode\n    type\n    value\n\n    }\n    sellingPrice {\n        \n    currencyCode\n    type\n    value\n\n    }\n    signings {\n        \n    discount {\n        \n    key\n    text\n\n    }\n    merchandise {\n        \n    key\n    text\n\n    }\n\n    }\n    trackingMetadata\n    size\n    url\n\n    }\n    recommendationRanking\n\n        }\n        pagination {\n            \n    currentPage {\n        \n    pageNumber\n    query\n    relativeUrl\n\n    }\n    nextPage {\n        \n    pageNumber\n    query\n    relativeUrl\n\n    }\n    previousPage {\n        \n    pageNumber\n    query\n    relativeUrl\n\n    }\n    totalItemCount\n    viewSize\n\n        }\n    }\n } }"

# Manually found that these specific querries result in articles that can be seperated in 4 the Target group categories
groupQuery = [
                ['Men', 'Women', 'Boys', 'Girls'], 
                ['categories<{catalog01_80}/categories<{catalog01_80_890}','categories<{catalog01_60}/categories<{catalog01_60_880}',
                'categories<{catalog01_100}/baby_geslacht>{jongens}','categories<{catalog01_100}/baby_geslacht>{meisjes}']
                ]

queries = {targetGroup: baseQuery.replace('**CATEGORYPLACEHOLDER**', targetGroupQuery) for targetGroup, targetGroupQuery in zip(*groupQuery)}

