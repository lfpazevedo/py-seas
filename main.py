import os
from datetime import datetime
import pandas as pd
import certifi

custom_tempdir = 'tmp'  # or any desired directory
if not os.path.exists(custom_tempdir):
    os.makedirs(custom_tempdir, exist_ok=True)

from src.data.holidays import (
    load_environment_variables,
    download_holiday_data,
    load_and_clean_data,
    create_holiday_summary,
    filter_holiday_summary,
    )

from src.genhol.genhol import (
    load_r_packages,
    create_holiday_dataframe,
    )

from src.data.pimpf import (
    fetch_data,
    convert_to_dataclasses,
    process_data,
    plot_data,
    CERT_PATH,
    )

from src.model.pimpf_sa import (
    run_x13_arima_analysis,
    print_x13_results,
    create_seasonally_adjusted_series,
    plot_comparison,
    )
    
from src.model.pimpf_sa_copy import (
    c,
    seasonal_func,
)

from dotenv import load_dotenv

load_dotenv()
# os.environ["X13_PATH"] = os.getenv("X13_PATH")
# os.environ["X13_PATH"] = r"C:\Projects\WinX13\x13as"

# def main():
"""Main function to execute the holiday data processing."""
load_environment_variables()

url = 'https://www.anbima.com.br/feriados/arqs/feriados_nacionais.xls'
tmp_path = download_holiday_data(url)

try:
    df_anbima = load_and_clean_data(tmp_path)
    df_holiday_summary = create_holiday_summary(df_anbima)

    start_date = pd.Timestamp("2001-01-01")
    end_date = pd.Timestamp(datetime(datetime.now().year + 1, 1, 1))

    df_filtered_holidays = filter_holiday_summary(df_holiday_summary, start_date, end_date)

    print(df_filtered_holidays)
finally:
    os.remove(tmp_path)

"""Main function to process holiday effects and create a DataFrame."""
utils, base, seasonal = load_r_packages()
holiday_df = create_holiday_dataframe(df_filtered_holidays, base, seasonal)
holiday_df['Year'] = pd.date_range(start='2001-01-01', periods=len(holiday_df), freq='MS').year.values
holiday_df['Month'] = pd.date_range(start='2001-01-01', periods=len(holiday_df), freq='MS').month.values
       
print(holiday_df.tail(24))

"""
Main execution function:
1. Fetch data from IBGE API.
2. Convert to dataclasses.
3. Process data and plot.
"""

# Configuration constants
CERT_PATH = certifi.where()
ROOT = "https://apisidra.ibge.gov.br/values/t/"
TABLE_CODE = "8888"
TERRITORIAL_LEVEL = "1"
IBGE_TERRITORIAL_CODE = "all"
VARIABLE = "12606,12607"
PERIOD = "all"
CLASSIFICATION = "544/129314"

data = fetch_data(
    root=ROOT,
    table_code=TABLE_CODE,
    territorial_level=TERRITORIAL_LEVEL,
    ibge_territorial_code=IBGE_TERRITORIAL_CODE,
    variable=VARIABLE,
    classification=CLASSIFICATION,
    periods=[PERIOD],
    cert_path=CERT_PATH,
)

# if not data:
#     print("No data returned from the API.")
#     return

dataclass_objects = convert_to_dataclasses(data)

# Optional: Print each dataclass instance
for obj in dataclass_objects:
    print(obj)

grouped_data, legends = process_data(dataclass_objects)
plot_data(grouped_data, legends)


#####
# X13-ARIMA-SEATS analysis
# x13_path = "C:\\Projects\\WinX13\\x13as"
key = '12606'
data = grouped_data[key]
series_12606 = pd.Series({date: value for date, value in data})   

outliers_type = [
    "AO",
    "LS",
    "TC",
]
months = ["Mar", "Apr", "May", "Nov", "Dec"]
years = ["2008", "2018", "2020"]

composed_outliers = [
    outliers_type[1] + years[0] + "." + months[3],
    outliers_type[2] + years[0] + "." + months[4],
    outliers_type[0] + years[1] + "." + months[2],
    outliers_type[0] + years[2] + "." + months[0],
    outliers_type[2] + years[2] + "." + months[1],
]
# Run X13-ARIMA analysis
results = seasonal_func(
    series=series_12606,
    seasonal=seasonal,
    base="year",  # Replace with the actual base value
    arima_model=c(0, 1, 1),
    transform_function="none",
    outliers_types="all",
    regression_variables=c("td", "easter[1]", composed_outliers),
    regression_usertype="holiday",
    xreg=holiday_df,
    forecast_maxback=12,
    forecast_maxlead=12,
)

# if __name__ == "__main__":
#     main()
