import duckdb
import logging

def newcol(con, color, name, dtype):
    con.execute(f"""ALTER TABLE {color}_trips
                        ADD COLUMN IF NOT EXISTS {name} {dtype};""")

try:
    con = duckdb.connect(database="emissions.duckdb",read_only=False)
    for color in ['yellow','green']:
        # emissions per trip
        # Add column to (color)_trips table
        # trip distance * co2 per mile for respective taxi type
        newcol(con, color, "trip_co2_kgs", "FLOAT")
        con.execute(f"""UPDATE {color}_trips
                        SET trip_co2_kgs = trip_distance *
                            (SELECT co2_grams_per_mile FROM vehicle_emissions
                            WHERE vehicle_type = '{color}_taxi') / 1000.0""")
        #print(con.execute(f"""SELECT trip_distance, trip_co2_kgs 
        #                  FROM {color}_trips LIMIT 3""").fetchall())
        # Average mph
        newcol(con, color, "avg_mph", "FLOAT")
        con.execute(f"""UPDATE {color}_trips
                    SET avg_mph = trip_distance / (DATE_DIFF('second', pickup_time, dropoff_time) / 3600.0);""")
        #print("Average mph")
        #print(con.execute(f"""SELECT trip_distance, pickup_time, dropoff_time, avg_mph 
        #            FROM {color}_trips LIMIT 3""").fetchall())
        # Date columns
        colnames = ["hour_of_day", "day_of_week", "week_of_year", "month_of_year"]
        cmd = ["DATE_PART('hour', pickup_time)", "DAYOFWEEK(pickup_time)", 
               "WEEKOFYEAR(pickup_time)", "MONTH(pickup_time)"]
        for colname, cmd in zip(colnames, cmd):
            newcol(con, color, colname, "INTEGER")
            con.execute(f"""UPDATE {color}_trips 
                        SET {colname} = {cmd};""")
            #print(f"{color} {colname}")
            #print(con.execute(f"""SELECT pickup_time, {colname} 
            #FROM {color}_trips ORDER BY RANDOM() LIMIT 3""").fetchall())
        

        
        
        
except Exception as e:
    print(f"Caught exception: {e}")