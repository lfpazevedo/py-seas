import os
import pandas as pd
import numpy as np
from datetime import datetime
from typing import List, Optional, Union
import rpy2.robjects as ro
from rpy2.robjects.packages import importr
from rpy2.robjects.vectors import StrVector
from rpy2.robjects import pandas2ri

from src.data.pimpf import (
    fetch_data,
    convert_to_dataclasses,
    process_data,
    plot_data,
    TerritorialData,
    CERT_PATH,
    ROOT,
    TABLE_CODE,
    TERRITORIAL_LEVEL,
    IBGE_TERRITORIAL_CODE,
    VARIABLE,
    PERIOD,
    CLASSIFICATION
    )

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

def load_r_packages():
    """Loads required R packages using rpy2."""
    return importr("utils"), importr("base"), importr("seasonal")

utils, base, seasonal = load_r_packages()

# =========================================================
# Import NSA and SA series from the IBGE API
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

dataclass_objects = convert_to_dataclasses(data)

# Prepare data for the DataFrame
data = [
    {"D3C": obj.D3C, "D2C": obj.D2C, "V": obj.V}
    for obj in dataclass_objects
]

df = pd.DataFrame(data)
df = df[1:]
df['D3C'] = pd.to_datetime(df['D3C'], format='%Y%m')
df = df.pivot(index='D3C', columns='D2C', values='V').reset_index()
df.columns = ['date', 'pimpf', 'pimpf_sa']

df_nsa = df[['date', 'pimpf']]
df_nsa_pimpf = df_nsa['pimpf']

# R data frame converted from a pandas data frame
with (ro.default_converter + pandas2ri.converter).context():
  df_nsa_converted = ro.conversion.get_conversion().py2rpy(df_nsa)
print(df_nsa_converted)
with (ro.default_converter + pandas2ri.converter).context():
  df_nsa_pimpf_converted = ro.conversion.get_conversion().py2rpy(df_nsa_pimpf)
print(df_nsa_pimpf_converted)

ts_r = ro.r('ts')
series_nsa = ts_r(df_nsa_pimpf_converted, frequency=12, start=2002)

# calling the R function base::summary
with (ro.default_converter + pandas2ri.converter).context():
  df_nsa_summary = base.summary(df_nsa)
print(df_nsa_summary)

# =========================================================

# =========================================================
# Import and process holiday data
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
df_holiday = create_holiday_dataframe(df_filtered_holidays, base, seasonal)
# df_holiday['Year'] = pd.date_range(start='2001-01-01', periods=len(df_holiday), freq='MS').year.values
# df_holiday['Month'] = pd.date_range(start='2001-01-01', periods=len(df_holiday), freq='MS').month.values
# df_holiday.tail(24)
# drop Easter
df_holiday = df_holiday.drop(columns=['Easter'])

# R data frame converted from a pandas data frame
with (ro.default_converter + pandas2ri.converter).context():
  df_holiday_converted = ro.conversion.get_conversion().py2rpy(df_holiday)
print(df_holiday_converted)

# calling the R function base::summary
with (ro.default_converter + pandas2ri.converter).context():
    df_holiday_summary = base.summary(df_holiday)
print(df_holiday_summary)

# IG Indústria Geral Aditivo (0 1 1) (0 1 1)
# Carnaval, Corpus Christi, Efeito Calendário, Páscoa[1],
# LS2008.Nov, TC2008.Dez, AO2018.Mai, AO2020.Mar, TC2020.Abr


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

def seasonal_func(
    series,
    # arima_model: str = "(0 1 1)",
    # transform_function: str = "",
    # outliers_types: str = "",
    # regression_variables: str = "",
    # regression_usertype: str = "",
    # # xreg: Optional[pd.DataFrame] = None,
    # forecast_maxback: int = 0,
    # forecast_maxlead: int = 0,
    # # check_print: str = "all",
    x11: str = "",
):
    _, _, seasonal = load_r_packages()
    
    return seasonal.seas(
        series,
        # arima_model=arima_model,
        # transform_function=transform_function,
        # outliers_types=outliers_types,
        # regression_variables=regression_variables,
        # regression_usertype=regression_usertype,
        # # xreg=xreg,
        # forecast_maxback=forecast_maxback,
        # forecast_maxlead=forecast_maxlead,
        # # check_print=check_print,
        x11=x11,
    )

results = seasonal_func(
    series=series_nsa,
    # arima_model="(0, 1, 1)(0, 1, 1)",
    # transform_function="none",
    # outliers_types="all",
    # regression_variables="('td','easter[1]','LS2008.Nov','TC2008.Dec','AO2018.May','AO2020.Mar','TC2020.Apr')",
    # regression_usertype="holiday",
    # xreg=df_holiday_converted,
    # forecast_maxback=12,
    # forecast_maxlead=12,
    # check_print="all",
    x11="",
)

ro.r('seas(AirPassengers)')   # ** THIS WORKS**

stl_r = ro.r('stl')
output_model_stl = stl_r(series_nsa, "periodic")  # ** THIS WORKS**

def seasonal_func(series,):
    seasonal = importr("seasonal")
    
    return seasonal.seas(series)

results = seasonal_func(
    series=series_nsa,
)