# #!/usr/bin/env python
import logging
import requests
import certifi
from dataclasses import dataclass
from typing import List, Union
import matplotlib.pyplot as plt
from datetime import datetime
from collections import defaultdict

@dataclass
class TerritorialData:
    """Dataclass to hold territorial data fetched from the IBGE API."""
    NC: str
    NN: str
    MC: str
    MN: str
    V: str
    D1C: str
    D1N: str
    D2C: str
    D2N: str
    D3C: str
    D3N: str
    D4C: str
    D4N: str


# Configuration constants
CERT_PATH = certifi.where()
ROOT = "https://apisidra.ibge.gov.br/values/t/"
TABLE_CODE = "8888"
TERRITORIAL_LEVEL = "1"
IBGE_TERRITORIAL_CODE = "all"
VARIABLE = "12606,12607"
PERIOD = "all"
CLASSIFICATION = "544/129314"


def fetch_data(
    root: str,
    table_code: str,
    territorial_level: str,
    ibge_territorial_code: str,
    variable: Union[str, List[str]],
    classification: str,
    periods: List[str],
    cert_path: str,
    timeout: int = 10,
) -> Union[List[dict], None]:
    """
    Fetch data from the IBGE API based on provided parameters.
    
    Args:
        root: Base URL for the API.
        table_code: The IBGE table code.
        territorial_level: The territorial level for the query.
        ibge_territorial_code: The IBGE territorial code (e.g., 'all').
        variable: A single variable code or a list of variable codes.
        classification: Classification parameters for the API query.
        periods: A list of periods to fetch.
        cert_path: Path to the certificate bundle.
        timeout: Request timeout in seconds.

    Returns:
        A list of dictionaries representing the fetched data,
        or None if the request failed.
    """
    periods_str = "-".join(periods)
    variables_str = "|".join(map(str, variable)) if isinstance(variable, list) else variable
    url = (
        f"{root}{table_code}/n{territorial_level}/{ibge_territorial_code}/"
        f"v/{variables_str}/p/{periods_str}/c{classification}"
    )

    try:
        response = requests.get(url, verify=cert_path, timeout=timeout)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching data from {url}: {e}")
        return None


def convert_to_dataclasses(data: List[dict]) -> List[TerritorialData]:
    """
    Convert a list of dictionaries to a list of TerritorialData dataclass instances.
    """
    return [TerritorialData(**item) for item in data]


def process_data(dataclass_objects: List[TerritorialData]):
    """
    Process TerritorialData objects to be plotted.
    Groups data by D2C and converts values and dates into proper formats.
    
    Returns:
        grouped_data: A dict mapping D2C -> List of (date, value) tuples
        legends: A dict mapping D2C -> D2N (for use in plot legends)
    """
    grouped_data = defaultdict(list)
    legends = {}

    for obj in dataclass_objects:
        try:
            date = datetime.strptime(str(obj.D3C), '%Y%m')
            value = float(obj.V)
            grouped_data[obj.D2C].append((date, value))
            legends[obj.D2C] = obj.D2N
        except (ValueError, TypeError):
            logging.warning(f"Skipping invalid data entry: D3C={obj.D3C}, V={obj.V}")

    # Sort values by date
    for D2C in grouped_data:
        grouped_data[D2C].sort(key=lambda x: x[0])
    
    return grouped_data, legends


def plot_data(grouped_data: dict, legends: dict):
    """
    Plot the processed data as a time-series graph.
    
    Args:
        grouped_data: A dictionary mapping D2C to a list of (date, value) tuples.
        legends: A dictionary mapping D2C to the corresponding legend label (D2N).
    """
    plt.figure(figsize=(10, 6))
    for D2C, values in grouped_data.items():
        dates, values_float = zip(*values) if values else ([], [])
        plt.plot(dates, values_float, label=legends.get(D2C, D2C))

    plt.xlabel('Date')
    plt.ylabel('Value (V)')
    plt.title('Time-Series Graph by D2N')
    plt.legend(title="D2N Attribute", loc='lower center', bbox_to_anchor=(0.5, -0.3))
    plt.tight_layout()
    plt.grid(True)
    plt.show()


def main():
    """
    Main execution function:
    1. Fetch data from IBGE API.
    2. Convert to dataclasses.
    3. Process data and plot.
    """
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

    if not data:
        print("No data returned from the API.")
        return

    dataclass_objects = convert_to_dataclasses(data)

    # Optional: Print each dataclass instance
    for obj in dataclass_objects:
        print(obj)

    grouped_data, legends = process_data(dataclass_objects)
    plot_data(grouped_data, legends)
