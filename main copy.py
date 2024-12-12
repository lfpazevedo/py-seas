import os
import requests
import tempfile
import pandas as pd
from rpy2.robjects.packages import importr
from rpy2.robjects.vectors import StrVector
from datetime import datetime
from dotenv import load_dotenv

utils = importr('utils')
base = importr('base')
seasonal = importr('seasonal')

load_dotenv()
os.environ["X13_PATH"] = os.getenv("X13_PATH")

# Example code to get your holiday data (as you had before)
url = 'https://www.anbima.com.br/feriados/arqs/feriados_nacionais.xls'
response = requests.get(url)
with tempfile.NamedTemporaryFile(suffix=".xls", delete=False) as tmp:
    tmp.write(response.content)
    tmp_path = tmp.name

df_anbima = pd.read_excel(tmp_path, header=0)
df_anbima.columns = ['Date', 'Day of the Week', 'Holiday']
df_anbima = df_anbima[df_anbima['Date'].apply(lambda x: isinstance(x, datetime))]
df_anbima['Date'] = pd.to_datetime(df_anbima['Date'])

df_holiday = pd.DataFrame(df_anbima['Date'].dt.year.unique(), columns=['Year'])
df_holiday['Days by Year'] = df_holiday['Year'].apply(lambda x: df_anbima['Date'].dt.year.value_counts().loc[x])
df_holiday['Carnival'] = df_anbima.loc[df_anbima['Holiday'] == 'Carnaval', 'Date'].groupby(df_anbima['Date'].dt.year).last().values
df_holiday['Easter'] = df_anbima.loc[df_anbima['Holiday'] == 'Paixão de Cristo', 'Date'].groupby(df_anbima['Date'].dt.year).last().values
df_holiday['Corpus'] = df_anbima.loc[df_anbima['Holiday'] == 'Corpus Christi', 'Date'].groupby(df_anbima['Date'].dt.year).last().values

df_holiday['Carnival'] = df_holiday['Carnival'].replace({
    pd.Timestamp('2022-03-01'): pd.Timestamp('2022-03-02'),
    pd.Timestamp('2003-03-04'): pd.Timestamp('2003-03-05'),
    pd.Timestamp('2014-03-04'): pd.Timestamp('2014-03-05')
})

start_date = pd.Timestamp("2001-01-01")
end_date = pd.Timestamp(datetime(datetime.now().year + 1, 1, 1))
df_holiday = df_holiday[(df_holiday['Year'] >= start_date.year) & (df_holiday['Year'] <= end_date.year)]

carnival_str = df_holiday['Carnival'].dt.strftime('%Y-%m-%d').tolist()
easter_str = df_holiday['Easter'].dt.strftime('%Y-%m-%d').tolist()
corpus_str = df_holiday['Corpus'].dt.strftime('%Y-%m-%d').tolist()

# Convert to an R character vector
r_carnival_char = StrVector(carnival_str)
r_easter_char = StrVector(easter_str)
r_corpus_char = StrVector(corpus_str)

r_carnival_dates = base.as_Date(r_carnival_char, format="%Y-%m-%d")
r_easter_dates = base.as_Date(r_easter_char, format="%Y-%m-%d")
r_corpus_dates = base.as_Date(r_corpus_char, format="%Y-%m-%d")

carnival = seasonal.genhol(r_carnival_dates, start=-4, end=-1, frequency=12, center="calendar")
easter = seasonal.genhol(r_easter_dates, start=-8, frequency=12, center="calendar")
corpus = seasonal.genhol(r_corpus_dates, start=1, end=3, frequency=12, center="calendar")

# Combine the results into a Pandas data frame
r_regs = pd.DataFrame({'Carnival': carnival, 'Easter': easter, 'Corpus': corpus})
