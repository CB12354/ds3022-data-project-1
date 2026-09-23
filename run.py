from load import load_parquet_files
from clean import clean_taxi_db
from transform import transform_taxi_columns
from analysis import analyze_taxi_co2

def pipeline():
    load_parquet_files()
    clean_taxi_db()
    transform_taxi_columns()
    analyze_taxi_co2()
    
if __name__ == "__main__":
    pipeline()