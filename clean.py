import duckdb
import logging

#Trips should be cleaned and checked for the following conditions (whether or not they exist):

#Remove any duplicate trips.
#Remove any trips with 0 passengers.
#Remove any trips 0 miles in length.
#Remove any trips longer than 100 miles in length.
#Remove any trips lasting more than 1 day in length (86400 seconds).


def clean_taxi_db():
    """
    Removes duplicate rows from the taxi data tables, as well as
    irrelevant data points such as fare resets (0 passengers, 0 miles)
    and outliers (>100 miles, >1-day trips)
    """
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    handler = logging.FileHandler('clean.log')
    handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

    logger.addHandler(handler)
    logger.propagate = False
    con = None
    try:
        con = duckdb.connect(database="emissions.duckdb",read_only=False)
        print("Connected to DDB instance - Clean")
        logger.info("Connected to DDB instance - Clean")
        # Drop duplicates
        for color in ['yellow','green']:
            print(f"Cleaning {color} taxis")
            logger.info(f"Cleaning {color} taxis")
            con.execute(f"DROP TABLE IF EXISTS {color};")
            con.execute(f"""CREATE TABLE {color} AS SELECT DISTINCT * FROM {color}_trips;""")
            # Check there are no duplicate rows in color
            ct_all = f"""Original table count: {con.execute(f"""SELECT COUNT(*) FROM {color}_trips;""").fetchone()[0]}"""
            print(ct_all)
            logger.info(ct_all)
            ct_dpc = f"""Dropped duplicates table count: {con.execute(f"""SELECT COUNT(*) FROM {color};""").fetchone()[0]}"""
            print(ct_dpc)
            logger.info(ct_dpc)
            
            # Drop 0-passenger trips
            con.execute(f"""DELETE FROM {color} WHERE passenger_count = 0;""")
            ct_psg = f"""0-Passenger row count: {con.execute(f"""SELECT COUNT(*) FROM {color} WHERE passenger_count = 0;""").fetchone()[0]}"""
            print(ct_psg)
            logger.info(ct_psg)
            
            # Drop trips of 0 miles and over 100 miles
            con.execute(f"DELETE FROM {color} WHERE trip_distance = 0 OR trip_distance > 100;")
            ct_dst = f"""distance = 0 or >100 row count: {con.execute(f"""SELECT COUNT(*) FROM {color} WHERE trip_distance = 0 OR trip_distance > 100;""").fetchone()[0]}"""
            print(ct_dst)
            logger.info(ct_dst)
            
            # Drop trips over 1 day long
            con.execute(f"DELETE FROM {color} WHERE DATE_DIFF('second', pickup_time, dropoff_time) > 86400;")
            
            ct_time = f""">1 day trip row count: {con.execute(f"""SELECT COUNT(*) FROM {color} WHERE DATE_DIFF('second', pickup_time, dropoff_time) > 86400;""").fetchone()[0]}"""
            print(ct_time)
            logger.info(ct_time)
            
            #double-check there are no rows with the removed conditions
            ban = con.execute(f"""SELECT COUNT(*) FROM {color} WHERE
                            passenger_count = 0 OR
                            trip_distance = 0 OR
                            trip_distance > 100 OR
                            DATE_DIFF('second', pickup_time, dropoff_time) > 86400;""").fetchone()[0]
            ct_ban = f"Double-checking for banned term rows: {ban}"
            print(ct_ban)
            logger.info(ct_ban)
            
            
            # Replace the original table with the cleaned one, then discard the new one
            con.execute(f"""
                        DELETE FROM {color}_trips;
                        INSERT INTO {color}_trips SELECT * FROM {color};
                        DROP TABLE {color};""")
            ct_del = f"""Original table count after replacement: {con.execute(f"""SELECT COUNT(*) FROM {color}_trips;""").fetchone()[0]}"""
            print(ct_del)
            logger.info(ct_del)
            
        
        
    except Exception as e:
        print(f"Caught exception: " + str(e))
        logger.error(f"Caught exception: {e}")
        exit()

if __name__ == "__main__":
    clean_taxi_db()