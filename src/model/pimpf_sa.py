import os
import pandas as pd
import statsmodels.api as sm
import matplotlib.pyplot as plt


def run_x13_arima_analysis(pim_nsa: pd.Series, genhol: pd.DataFrame) -> sm.tsa.x13_arima_analysis:
    """
    Run X13-ARIMA-SEATS seasonal adjustment on the provided series using genhol regressors.
    
    Args:
        pim_nsa: A pandas Series of non-seasonally adjusted data (e.g., industrial production index).
        genhol: DataFrame containing holiday regressors.

    Returns:
        X13-ARIMA-SEATS results object.
    """
    # # Get the X13_PATH from the environment variable
    # x13_path = os.getenv("X13_PATH")
    
    # if not x13_path:
    #     raise EnvironmentError("The X13_PATH environment variable is not set or invalid.")
    
    # Run X13-ARIMA-SEATS analysis
    results = sm.tsa.x13_arima_analysis(
        endog=pim_nsa,
        maxorder=(1, 1),
        diff=(1, 1),
        exog=genhol,
        log=False,
        outlier=True,
        trading=True,
        retspec=True,
        x12path=None,  # Pass the dynamic path
        prefer_x13=True,
    )
    return results


def print_x13_results(results: sm.tsa.x13_arima_analysis):
    """
    Print selected parts of the X13-ARIMA-SEATS results.
    
    Args:
        results: X13ARIMAResults object from X13-ARIMA-SEATS analysis.
    """
    # X13 results are separated by form feeds (\x0c)
    parts = results.results.split('\x0c')

    # Print some parts as needed
    # Adjust indices depending on what you'd like to see
    if len(parts) > 0:
        print(parts[0])  # For example, model summary
    if len(parts) > 3:
        print(parts[3])  # Another section of interest


def create_seasonally_adjusted_series(results: sm.tsa.x13_arima_analysis, pim_sa_index: pd.Index) -> pd.DataFrame:
    """
    Create a DataFrame with the seasonally adjusted series from the X13 results.
    
    Args:
        results: X13ARIMAResults object from X13-ARIMA-SEATS analysis.
        pim_sa_index: Index for aligning the resulting DataFrame with another series.

    Returns:
        A DataFrame containing the seasonally adjusted values with appropriate indexing.
    """
    pim_sa_genhol = pd.Series(results.seasadj.values, index=pim_sa_index)
    pim_sa_genhol = pim_sa_genhol.to_frame(name='pim_sa_genhol')
    return pim_sa_genhol


def plot_comparison(ibge_genhol: pd.DataFrame):
    """
    Plot the original and holiday-adjusted seasonally adjusted industrial production series.
    
    Args:
        ibge_genhol: DataFrame containing 'date', 'pim_sa', and 'pim_sa_genhol' columns.
    """
    plt.plot(ibge_genhol['date'], ibge_genhol['pim_sa'], color='red')
    plt.plot(ibge_genhol['date'], ibge_genhol['pim_sa_genhol'], color='blue')
    plt.title('Industrial Production', fontsize=14)
    plt.xlabel('Year', fontsize=14)
    plt.ylabel('Index', fontsize=14)
    plt.legend(['SA_IBGE', 'SA_Genhol'])
    plt.grid(True)
    plt.show()


