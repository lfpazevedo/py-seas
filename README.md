# py-seas

Seasonal adjustment using Genhol in R.

## Project Structure

py-seas/ ├── __init__.py ├── pycache/ ├── .env ├── .gitignore ├── genhol_df.py ├── ibge_compare.py ├── pyproject.toml ├── README.md ├── src/ │ ├── __init__.py │ ├── pycache/ │ ├── data/ │ │ ├── holidays.py │ ├── genhol/ │ │ └── genhol.py │  └── uv.lock


## Usage

Running the Genhol script
To run the Genhol script, use:

uv run df_genhol.py


Running the IBGE_compare script
To run the IBGE compare, use:

uv run ibge_compare.py


## Dependencies
The project dependencies are listed in the pyproject.toml file and include:

ipykernel==6.29.5
requests==2.32.3
pandas==2.2.3
rpy2==3.5.17
python-dotenv==1.0.1
xlrd==2.0.1
matplotlib==3.9.3
statsmodels==0.14.4


## License
This project is licensed under the MIT License.