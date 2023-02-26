from camelot import read_pdf

# Get all the tables within the file
all_tables = read_pdf('./data/bmo_chq_eStatement_2022-11-04.pdf', pages = 'all')

# Show the total number of tables in the file
print("Total number of table: {}".format(all_tables.n))

# print all the tables in the file
for t in range(all_tables.n):
    print("Table {}".format(t))
    print((all_tables[t].df).head())

# Requires tk, ghostscript, opencv-python
# Total number of table: 0