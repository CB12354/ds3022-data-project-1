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
    print(con.execute("""
                SELECT DISTINCT MONTH(pickup_time) AS month FROM yellow_trips ORDER BY month;
                """).fetchall())
    print(con.execute("""
                SELECT DISTINCT MONTH(pickup_time) AS month FROM green_trips ORDER BY month;
                """).fetchall())
except Exception as e:
    print(f"Caught exception: " + str(e))
    exit()

#if __name__ == "__main__":