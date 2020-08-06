import collect.collect as c
import os
import pymongo


# Extract and process data
df_can, df_map_CA, df_timeorder, df_world, df_map_world, df_timeorder_world = c.format_data()

# Store data in Mongodb cloud database
connectionURL = os.getenv('MONGO_URL').strip("\"")
db_client = pymongo.MongoClient(connectionURL)
c.store_data(db_client, df_can, df_map_CA, df_timeorder, df_world, df_map_world, df_timeorder_world)
