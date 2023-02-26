from tabula import read_pdf
from tabulate import tabulate
import pandas as pd
import io

# Read the only the page of the file
food_calories = read_pdf('./data/bmo_chq_eStatement_2022-11-04.pdf',pages = 2,
                         multiple_tables = True, stream = True)

# Transform the result into a string table format
table = tabulate(food_calories)

# Transform the table into dataframe
df = pd.read_fwf(io.StringIO(table))

# Save the final result as excel file
df.to_excel("./data/tabulate_result.xlsx")

# Needs Java