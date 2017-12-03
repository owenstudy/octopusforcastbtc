import pandas as pd

pricehis= pd.read_csv('pricehistory.log','|')

# print(pricehis)
print(pricehis.ix[1:3,3:6])