import duckdb
import logging

#Trips should be cleaned and checked for the following conditions (whether or not they exist):

#Remove any duplicate trips.
#Remove any trips with 0 passengers.
#Remove any trips 0 miles in length.
#Remove any trips longer than 100 miles in length.
#Remove any trips lasting more than 1 day in length (86400 seconds).

con = None
try:
    con = duckdb.connect(database="emissions.duckdb",read_only=False)
    # Drop duplicates
    for color in ['yellow','green']:
        print(f"Taxi color: {color}")
        con.execute(f"DROP TABLE IF EXISTS {color};")
        con.execute(f"""CREATE TABLE {color} AS SELECT DISTINCT * FROM {color}_trips;""")
        # Check there are no duplicate rows in color
        print(con.execute(f"""SELECT COUNT(*) FROM {color}_trips;""").fetchone()[0])
        print(con.execute(f"""SELECT COUNT(*) FROM {color};""").fetchone()[0])
        
        # Drop 0-passenger trips
        con.execute(f"""DELETE FROM {color} WHERE passenger_count = 0;""")
        print(con.execute(f"""SELECT COUNT(*) FROM {color};""").fetchone()[0])
        
        # Drop trips of 0 miles and over 100 miles
        con.execute(f"DELETE FROM {color} WHERE trip_distance = 0 OR trip_distance > 100;")
        print(con.execute(f"""SELECT COUNT(*) FROM {color};""").fetchone()[0])
        
        # Drop trips over 1 day long
        con.execute(f"DELETE FROM {color} WHERE DATE_DIFF('second', pickup_time, dropoff_time) > 86400;")
        print(con.execute(f"""SELECT COUNT(*) FROM {color};""").fetchone()[0])
        
        #double-check there are no rows with the removed conditions
        print(con.execute(f"""SELECT COUNT(*) FROM {color} WHERE
                          passenger_count = 0 OR
                          trip_distance = 0 OR
                          trip_distance > 100 OR
                          DATE_DIFF('second', pickup_time, dropoff_time) > 86400;""").fetchone()[0])
        
        # Replace the original table with the new one, then discard the new one
        con.execute(f"""
                    DELETE FROM {color}_trips;
                    INSERT INTO {color}_trips SELECT * FROM {color};
                    DROP TABLE {color};""")
        print(con.execute(f"""SELECT COUNT(*) FROM {color}_trips;""").fetchone()[0])
        
    
    
except Exception as e:
    print(f"Caught exception: " + str(e))
    exit()

#if __name__ == "__main__":