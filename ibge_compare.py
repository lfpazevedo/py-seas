import pandas as pd
import matplotlib.pyplot as plt
from genhol_df import main

# import excel url
# https://ftp.ibge.gov.br/Industrias_Extrativas_e_de_Transformacao/Pesquisa_Industrial_Mensal_Producao_Fisica/Material_de_apoio/2024_Pesos_ajuste_sazonal_series_iniciadas_em_2002.xls

df_2024_Pesos_ajuste_sazonal_series_iniciadas_em_2002 = pd.read_excel('https://ftp.ibge.gov.br/Industrias_Extrativas_e_de_Transformacao/Pesquisa_Industrial_Mensal_Producao_Fisica/Material_de_apoio/2024_Pesos_ajuste_sazonal_series_iniciadas_em_2002.xls')
df_2024_Pesos_ajuste_sazonal_series_iniciadas_em_2002 = df_2024_Pesos_ajuste_sazonal_series_iniciadas_em_2002.rename(columns=df_2024_Pesos_ajuste_sazonal_series_iniciadas_em_2002.iloc[0]).drop(df_2024_Pesos_ajuste_sazonal_series_iniciadas_em_2002.index[0])
df_2024_Pesos_ajuste_sazonal_series_iniciadas_em_2002 = df_2024_Pesos_ajuste_sazonal_series_iniciadas_em_2002.drop(df_2024_Pesos_ajuste_sazonal_series_iniciadas_em_2002.index[-1])
df_2024_Pesos_ajuste_sazonal_series_iniciadas_em_2002 = df_2024_Pesos_ajuste_sazonal_series_iniciadas_em_2002.rename(columns={'ANO': 'Year', 'MÊS': 'Month', 'Peso Carnaval': 'Carnival_IBGE', 'Peso Corpus Christi': 'Corpus_IBGE'})
print(df_2024_Pesos_ajuste_sazonal_series_iniciadas_em_2002)


# Carnival on Tuesday
r_regs = main()
print(r_regs)


# Carnival on Wednesday for 2022, 2003, 2014, and 2025
date_replacements = {
    pd.Timestamp('2022-03-01'): pd.Timestamp('2022-03-02'),
    pd.Timestamp('2003-03-04'): pd.Timestamp('2003-03-05'),
    pd.Timestamp('2014-03-04'): pd.Timestamp('2014-03-05'),
    pd.Timestamp('2025-03-04'): pd.Timestamp('2025-03-05'),
}

r_regs_adjusted = main(date_replacements)
print(r_regs_adjusted)

fig, axs = plt.subplots(2, 1, figsize=(12, 8))

axs[0].plot(df_2024_Pesos_ajuste_sazonal_series_iniciadas_em_2002['Year'].astype(str) + '-' + df_2024_Pesos_ajuste_sazonal_series_iniciadas_em_2002['Month'].astype(str), df_2024_Pesos_ajuste_sazonal_series_iniciadas_em_2002['Carnival_IBGE'], label='IBGE')
axs[0].plot(r_regs['Year'].astype(str) + '-' + r_regs['Month'].astype(str), r_regs['Carnival'], label='Tuesdays')
axs[0].set_title('Carnival - Holiday on Tuesday vs. Wednesday for 2022, 2003, 2014, and 2025')
axs[0].set_xticks(axs[0].get_xticks()[::24])  # Reduce number of ticks
axs[0].legend()

axs[1].plot(df_2024_Pesos_ajuste_sazonal_series_iniciadas_em_2002['Year'].astype(str) + '-' + df_2024_Pesos_ajuste_sazonal_series_iniciadas_em_2002['Month'].astype(str), df_2024_Pesos_ajuste_sazonal_series_iniciadas_em_2002['Carnival_IBGE'], label='IBGE')
axs[1].plot(r_regs_adjusted['Year'].astype(str) + '-' + r_regs_adjusted['Month'].astype(str), r_regs_adjusted['Carnival'], label='Adjusted')
axs[1].set_xticks(axs[1].get_xticks()[::24])  # Reduce number of ticks
axs[1].legend()
axs[1].legend()

plt.show()


fig, ax = plt.subplots(1, 1, figsize=(12, 8))

ax.plot(
    df_2024_Pesos_ajuste_sazonal_series_iniciadas_em_2002['Year'].astype(str) + '-' + 
    df_2024_Pesos_ajuste_sazonal_series_iniciadas_em_2002['Month'].astype(str), 
    df_2024_Pesos_ajuste_sazonal_series_iniciadas_em_2002['Corpus_IBGE'], 
    label='IBGE'
)
ax.plot(
    r_regs['Year'].astype(str) + '-' + 
    r_regs['Month'].astype(str), 
    r_regs['Corpus'], 
    label='No adjustment'
)
ax.set_title('Corpus - No adjustment')
ax.set_xticks(ax.get_xticks()[::24])  # Reduce number of ticks
ax.legend()

plt.show()
