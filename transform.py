import duckdb
import logging

logger = None

def newcol(con, color, name, dtype):
    """
    Adds a new column to a chosen taxi data table.
    
    Arguments:
    con -- The connection to the DuckDB database. 
    color -- The color of taxi. (String)
    name -- The name of the new column. (String)
    dtype -- The data type of the new column, in SQL. (String)
    """
    s = f"Making new column in {color}_trips if not exists: {name}, {dtype}"
    print(s)
    logger.info(s)
    con.execute(f"""ALTER TABLE {color}_trips
                        ADD COLUMN IF NOT EXISTS {name} {dtype};""")

def transform_taxi_columns():
    """
    Adds new columns to the taxi data tables: Kilograms of CO2 produced
    by the trip, average mph of the trip, hour of day, day of
    week, week of year, month of year
    """
    global logger
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    handler = logging.FileHandler('transform.log')
    handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

    logger.addHandler(handler)
    logger.propagate = False
    con = None
    try:
        con = duckdb.connect(database="emissions.duckdb",read_only=False)
        print("Connected to DuckDB instance - Transform")
        logger.info("Connected to DuckDB instance - Transform")
        for color in ['yellow','green']:
            # emissions per trip
            # Add column to (color)_trips table
            # trip distance * co2 per mile for respective taxi type
            newcol(con, color, "trip_co2_kgs", "FLOAT")
            con.execute(f"""UPDATE {color}_trips
                            SET trip_co2_kgs = trip_distance *
                                (SELECT co2_grams_per_mile FROM vehicle_emissions
                                WHERE vehicle_type = '{color}_taxi') / 1000.0""")
            kg_str = "Added data for column trip_co2_kgs"
            print(kg_str)
            logger.info(kg_str)
            
            # Average mph
            newcol(con, color, "avg_mph", "FLOAT")
            con.execute(f"""UPDATE {color}_trips
                        SET avg_mph = trip_distance / (DATE_DIFF('second', pickup_time, dropoff_time) / 3600.0);""")
            mph_str = "Added data for column avg_mph"
            print(mph_str)
            logger.info(mph_str)
            # Date columns
            colnames = ["hour_of_day", "day_of_week", "week_of_year", "month_of_year"]
            parts = ['hour', 'dow', 'week', 'month']
            for colname, part in zip(colnames, parts):
                newcol(con, color, colname, "INTEGER")
                con.execute(f"""UPDATE {color}_trips 
                            SET {colname} = DATE_PART('{part}', pickup_time);""")
                time_str = f"Added data for column {colname}"
                print(time_str)
                logger.info(time_str)
            
    except Exception as e:
        print(f"Caught exception: {e}")
        logger.error(f"Caught exception: {e}")
        exit()
        
if __name__ == "__main__":
    transform_taxi_columns()