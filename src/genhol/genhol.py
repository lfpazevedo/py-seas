import pandas as pd
from rpy2.robjects.packages import importr
from rpy2.robjects.vectors import StrVector

def load_r_packages():
    """Loads required R packages using rpy2."""
    return importr('utils'), importr('base'), importr('seasonal')

def convert_dates_to_r_format(dates, base):
    """Converts a list of pandas datetime dates to R Date format.

    Args:
        dates (list): A list of pandas datetime dates.
        base (R object): The `base` package from R.

    Returns:
        R object: An R Date vector.
    """
    str_dates = dates.dt.strftime('%Y-%m-%d').tolist()
    r_char_vector = StrVector(str_dates)
    return base.as_Date(r_char_vector, format="%Y-%m-%d")

def generate_holiday_effects(r_dates, seasonal, start, end=None, frequency=12, center="calendar"):
    """Generates holiday effects using the seasonal package in R.

    Args:
        r_dates (R object): R Date vector of holiday dates.
        seasonal (R object): The `seasonal` package from R.
        start (int): The start offset for the holiday effect.
        end (int, optional): The end offset for the holiday effect. Defaults to None.
        frequency (int, optional): The frequency for the effect. Defaults to 12.
        center (str, optional): The centering method. Defaults to "calendar".

    Returns:
        R object: Generated holiday effect.
    """
    if end is not None:
        return seasonal.genhol(r_dates, start=start, end=end, frequency=frequency, center=center)
    return seasonal.genhol(r_dates, start=start, frequency=frequency, center=center)

def create_holiday_dataframe(df_holiday, base, seasonal):
    """Creates a Pandas DataFrame with holiday effects for Carnival, Easter, and Corpus.

    Args:
        df_holiday (pd.DataFrame): DataFrame containing holiday dates.
        base (R object): The `base` package from R.
        seasonal (R object): The `seasonal` package from R.

    Returns:
        pd.DataFrame: DataFrame with holiday effects.
    """
    carnival_dates = convert_dates_to_r_format(df_holiday['Carnival'], base)
    easter_dates = convert_dates_to_r_format(df_holiday['Easter'], base)
    corpus_dates = convert_dates_to_r_format(df_holiday['Corpus'], base)

    carnival = generate_holiday_effects(carnival_dates, seasonal, start=-4, end=-1)
    easter = generate_holiday_effects(easter_dates, seasonal, start=-8)
    corpus = generate_holiday_effects(corpus_dates, seasonal, start=1, end=3)

    return pd.DataFrame({
        'Carnival': carnival,
        'Easter': easter,
        'Corpus': corpus,
    })
