
import sqlite3
import pandas as pd

# Connect to the database
conn = sqlite3.connect("anime.db")

# =================================================================
# Query the database and convert to DataFrame
query = '''
SELECT workId, engName, synonymsName, jpName, episodes, genres
FROM animeList
'''
df = pd.read_sql_query(query, conn)
# Write DataFrame to CSV
df.to_csv("animeListGenres.csv", index=False)
# =================================================================


# =================================================================
# Define the SQL query
query = '''
SELECT workId, aired, genres
FROM animeList
'''
# Load the data into a pandas DataFrame
df = pd.read_sql_query(query, conn)
# Write the data to a CSV file
df.to_csv('animeList.csv', index=False)
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
df.to_csv('animeReviewsOrderByTime.csv', index=False)
# =================================================================

# Don't forget to close the connection
conn.close()
