import pandas as pd
import numpy as np
import collections
from datetime import datetime, timedelta

def main():
    df = load_data()
    last_30 = df.loc[df['Submit time'] > "1/1/2024 11:45:18"]
    print(last_30['Style Number'].value_counts()[:10])
    
def load_data() -> pd.DataFrame:
    # Load the two csv files downloaded from separate google sheets tabs
    shipout_history_path = "C:\\Users\\order\\Documents\\marathon_sports\\shipout_analyzer\\Shipout Tracking Sheet - Shipout History.csv"
    current_response_path = "C:\\Users\\order\\Documents\\marathon_sports\\shipout_analyzer\\Shipout Tracking Sheet - Form Response 8.csv"
    history_df = csv_to_df(shipout_history_path)
    current_df = csv_to_df(current_response_path)

    current_df['Reason'].value_counts().to_csv('reasons.csv')

    # combine the two into one dataframe
    combined_df = pd.concat([history_df, current_df])

    # Clean up
    combined_df.drop(["Current Store Email Address", "Shipping Store Email Address", "Notes", "RMA'd", "Ship Date", "Tracking Number", "Notes", "Notes.1"], axis=1, inplace=True)
    combined_df.rename(columns={"Unnamed: 0": "Submit time"}, inplace=True)

    # datetime = combined_df["Submit time"].apply(lambda x: pd.to_datetime(x, format='%m/%d/%Y %H:%M:%S'))
    # combined_df["Submit time"] = datetime
    
    return combined_df


def csv_to_df(path: str) -> pd.DataFrame:
    df = pd.read_csv(path, dtype=str)
    return df



main()
