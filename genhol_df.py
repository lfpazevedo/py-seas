import pandas as pd
from datetime import datetime
from src.genhol.genhol import (
    fetch_holiday_data,
    process_holiday_data,
    summarize_holidays,
    replace_dates,
    filter_holidays_by_year,
    convert_dates_to_r_vector,
    generate_holiday_effects,
)

def main(date_replacements=None):
    # URL for holiday data
    url = 'https://www.anbima.com.br/feriados/arqs/feriados_nacionais.xls'

    # Fetch and process holiday data
    raw_data = fetch_holiday_data(url)
    df_holiday = process_holiday_data(raw_data)
    df_holiday = summarize_holidays(df_holiday)

    # Replace specific dates
    df_holiday = replace_dates(df_holiday, date_replacements)

    # Filter holidays by year range
    start_date = pd.Timestamp("2001-01-01")
    end_date = pd.Timestamp(datetime(datetime.now().year + 1, 1, 1))
    df_holiday = filter_holidays_by_year(df_holiday, start_date, end_date)

    # Convert to R vectors and validate
    r_carnival_char = convert_dates_to_r_vector(df_holiday, 'Carnival')
    r_corpus_char = convert_dates_to_r_vector(df_holiday, 'Corpus')

    # Generate holiday effects
    carnival = generate_holiday_effects(r_carnival_char, start=-4, end=-1, frequency=12, center="calendar")
    corpus = generate_holiday_effects(r_corpus_char, start=1, end=3, frequency=12, center="calendar")

    # Combine results
    r_regs = pd.DataFrame({'Carnival': carnival, 'Corpus': corpus})

    r_regs['Year'] = pd.date_range(start='2001-01-01', periods=len(r_regs), freq='MS').year
    r_regs['Month'] = pd.date_range(start='2001-01-01', periods=len(r_regs), freq='MS').month

    r_regs = r_regs[['Year', 'Month', 'Carnival', 'Corpus']]

    return r_regs


if __name__ == "__main__":
    # Define date replacements
    date_replacements = {
        pd.Timestamp('2022-03-01'): pd.Timestamp('2022-03-02'),
        pd.Timestamp('2003-03-04'): pd.Timestamp('2003-03-05'),
        pd.Timestamp('2014-03-04'): pd.Timestamp('2014-03-05'),
        pd.Timestamp('2025-03-04'): pd.Timestamp('2025-03-05'),
    }
    
    # Call main with date replacements
    r_regs = main(date_replacements)
    print(r_regs)
