
import sqlite3
import pandas as pd

# Connect to the database
conn = sqlite3.connect("anime.db")

# =================================================================
# Define the SQL query
query = '''
SELECT *
FROM animeList
'''
# Load the data into a pandas DataFrame
df = pd.read_sql_query(query, conn)
# Write the data to a CSV file
df.to_csv('anime_list.csv', index=False, encoding='utf-8-sig')
# =================================================================

# =================================================================
# Define the SQL query
query = '''
SELECT * 
FROM reviews 
ORDER BY postTime
'''
# Load the data into a pandas DataFrame
df = pd.read_sql_query(query, conn)
# Drop the columns that you don't want in your CSV
df = df.drop(columns=['reviewerProfileUrl', 'reviewerImageUrl'])
# Write the data to a CSV file
df.to_csv('reviews.csv', index=False, encoding='utf-8-sig')
# =================================================================

# Don't forget to close the connection
conn.close()
