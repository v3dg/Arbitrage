import pandas as pd
df= pd.read_csv('arbitrage_opportunities.csv')
df.to_html('grades.html')