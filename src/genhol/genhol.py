import os
import requests
import tempfile
import pandas as pd
from rpy2.robjects.packages import importr
from rpy2.robjects.vectors import StrVector
from datetime import datetime
from dotenv import load_dotenv

# Load R packages
utils = importr('utils')
base = importr('base')
seasonal = importr('seasonal')

# Load environment variables
load_dotenv()
os.environ["X13_PATH"] = os.getenv("X13_PATH")

def fetch_holiday_data(url: str) -> pd.DataFrame:
    """Fetch holiday data from a URL and return as a DataFrame."""
    response = requests.get(url)
    with tempfile.NamedTemporaryFile(suffix=".xls", delete=False) as tmp:
        tmp.write(response.content)
        tmp_path = tmp.name
    return pd.read_excel(tmp_path, header=0)

def process_holiday_data(df: pd.DataFrame) -> pd.DataFrame:
    """Process raw holiday data into a structured DataFrame."""
    df.columns = ['Date', 'Day of the Week', 'Holiday']
    df = df.loc[df['Date'].apply(lambda x: isinstance(x, datetime))]
    df.loc[:, 'Date'] = pd.to_datetime(df['Date'])
    return df

def summarize_holidays(df: pd.DataFrame) -> pd.DataFrame:
    """Create a summary DataFrame with holidays grouped by year."""
    # Ensure 'Date' column is datetime
    df = df.copy()  # Avoid modifying the original DataFrame
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')  
    
    # Create a DataFrame with unique years
    unique_years = df['Date'].dt.year.unique()
    df_holiday = pd.DataFrame({'Year': unique_years})
    
    # Add days by year
    year_counts = df['Date'].dt.year.value_counts().to_dict()
    df_holiday['Days by Year'] = df_holiday['Year'].map(lambda x: year_counts.get(x, 0))
    
    # Process each holiday
    holidays = ['Carnaval', 'Paixão de Cristo', 'Corpus Christi']
    names = ['Carnival', 'Easter', 'Corpus']
    for holiday, name in zip(holidays, names):
        grouped = df.loc[df['Holiday'] == holiday].groupby(df['Date'].dt.year)['Date'].last()
        df_holiday[name] = df_holiday['Year'].map(grouped)
    
    return df_holiday

def replace_dates(df: pd.DataFrame, replacements: dict = None) -> pd.DataFrame:
    """Replace specific holiday dates in the DataFrame."""
    if replacements:
        df['Carnival'] = df['Carnival'].replace(replacements)
    return df

def filter_holidays_by_year(df: pd.DataFrame, start_date: pd.Timestamp, end_date: pd.Timestamp) -> pd.DataFrame:
    """Filter holidays by a given year range."""
    return df[(df['Year'] >= start_date.year) & (df['Year'] <= end_date.year)]

def convert_dates_to_r_vector(df: pd.DataFrame, column: str) -> StrVector:
    valid_dates = df[column].dropna()
    if valid_dates.empty:
        raise ValueError(f"The column {column} contains no valid dates.")
    return StrVector(valid_dates.dt.strftime('%Y-%m-%d').tolist())

def generate_holiday_effects(date_vector, start, end, frequency, center):
    """Generate holiday effects for seasonal adjustment using R."""
    if date_vector is None or len(date_vector) == 0:
        raise ValueError("Date vector is empty or None.")
    r_dates = base.as_Date(date_vector, format="%Y-%m-%d")
    return seasonal.genhol(r_dates, start=start, end=end, frequency=frequency, center=center)
