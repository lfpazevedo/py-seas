import os
import requests
import tempfile
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv


def load_environment_variables():
    """Loads environment variables from a .env file."""
    load_dotenv()
    os.environ["X13_PATH"] = os.getenv("X13_PATH")


def download_holiday_data(url):
    """Downloads the holiday data from the specified URL and saves it to a temporary file.

    Args:
        url (str): The URL to download the data from.

    Returns:
        str: The path to the temporary file containing the downloaded data.
    """
    response = requests.get(url)
    response.raise_for_status()
    with tempfile.NamedTemporaryFile(suffix=".xls", delete=False) as tmp:
        tmp.write(response.content)
        return tmp.name


def load_and_clean_data(file_path):
    """Loads and cleans the holiday data from the specified file.

    Args:
        file_path (str): The path to the file containing the holiday data.

    Returns:
        pd.DataFrame: A cleaned DataFrame containing the holiday data.
    """
    df = pd.read_excel(file_path, header=0)
    df.columns = ["Date", "Day of the Week", "Holiday"]
    df = df[df["Date"].apply(lambda x: isinstance(x, datetime))]
    df["Date"] = pd.to_datetime(df["Date"])
    return df


def create_holiday_summary(df):
    """Creates a summary DataFrame containing holiday information by year.

    Args:
        df (pd.DataFrame): The DataFrame containing cleaned holiday data.

    Returns:
        pd.DataFrame: A summary DataFrame with holiday details by year.
    """
    df_summary = pd.DataFrame(df["Date"].dt.year.unique(), columns=["Year"])
    df_summary["Days by Year"] = df_summary["Year"].apply(
        lambda x: df["Date"].dt.year.value_counts().loc[x]
    )

    for holiday_name, column_name in [
        ("Carnaval", "Carnival"),
        ("Paixão de Cristo", "Easter"),
        ("Corpus Christi", "Corpus"),
    ]:
        df_summary[column_name] = (
            df.loc[df["Holiday"] == holiday_name, "Date"]
            .groupby(df["Date"].dt.year)
            .last()
            .values
        )

    # df_summary['Carnival'] = df_summary['Carnival'].replace({
    #     pd.Timestamp('2022-03-01'): pd.Timestamp('2022-03-02'),
    #     pd.Timestamp('2003-03-04'): pd.Timestamp('2003-03-05'),
    #     pd.Timestamp('2014-03-04'): pd.Timestamp('2014-03-05')
    # })

    return df_summary


def filter_holiday_summary(df_summary, start_date, end_date):
    """Filters the holiday summary DataFrame based on the specified date range.

    Args:
        df_summary (pd.DataFrame): The summary DataFrame with holiday data.
        start_date (pd.Timestamp): The start date for the filter.
        end_date (pd.Timestamp): The end date for the filter.

    Returns:
        pd.DataFrame: The filtered holiday summary DataFrame.
    """
    return df_summary[
        (df_summary["Year"] >= start_date.year) & (df_summary["Year"] <= end_date.year)
    ]
