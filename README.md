# bankstate

Bank Statement Conversion for Import Into Home Finance Software

When doing a budget, the first step is invariably to collect at least a year's worth of data to form a reliable basis for the budget. Unfortunately, few banking institutions provide more than a few months of data in any of the download formats supported by home finance software. The first time budgeter is forced to download PDF statements from their accounts and somehow convert them for import into their home finance software. At least one of the commercial finance packages provide OCR of scanned statements (Quicken), but none of the free ones that I checked (HomeBank, GnuCash, MoneyManagementEX). In any case, the PDF files allow extraction of the text data without having to OCR them, so this is the preferred method.

## License

Copyright (C) 2017, 2023 Jeremy Squires <jms@mailforce.net>

License: <https://opensource.org/licenses/MIT>

## Scripts

pdf2txt.py

Reads PDF bank and mastercard statements and directly outputs a CSV format that can be imported into home finance software

stmt2csv.py

Converts text copied from PDF bank statements into a CSV or TSV format that can be imported into home finance software

## Supported Data Formats

* Bank of Montreal (BMO) bank account and credit card statements in PDF format
* Royal Bank of Canada (RBC) bank account and credit card statements in PDF format

Input to the stmt2csv.py script is manually copy/pasted from PDF files, so it is technically possible to create the input files from any source.

Since pdf2txt.py reads the PDF directly, it is the preferred method, requiring less manual intervention. However, in cases where the format of the PDFs change or are sourced from other banks, the manual copy method can still be used.

Generated CSV files follow the CSV RFC: <https://tools.ietf.org/html/rfc4180> and contain columns that in general match the input files, but with some cleanups to make import easier. Generated TSV files replace commas for tabs, which is useful when fields often contain commas.

## pdf2txt.py

### Requirements

* Python 3.8
* pipenv

### Process

* git clone git@github.com:jeremysquires/bankstate.git
* cd bankstate
* pipenv install --dev
* pipenv shell
* python pdf2txt.py filename.pdf filetype output.tsv
  * Where: filetype = [ bmo_bank | bmo_card | rbc_bank | rbc_card ]
* Open TSV in LibreOffice/Excel to verify it has the correct structure
* Import Into Budgeting Software

## Import Into Budgeting Software

For financial packages with flexible CSV/TSV import (MoneyManagementEX, GnuCash):

Open the file and use the header column mapping feature to set, at a minimum, maps of the following columns to corresponding columns in the software.

### Credit Cards

* Date
* Payee
* Amount (+/-)

### Checking

* Date
* Payee
* Withdrawal
* Deposit

All the other fields can be mapped to "Don't Care"

TIP: There is time to be spared in MoneyManagementEX in doing the following:

1. Import the CSV/TSV
2. Delete all the imported records
3. Tools, Organize Payees, set the Default Category for each Payee
4. Re-import the same CSV/TSV again (with the default category set correctly)

For HomeBank users:

1. Import resulting CSV/TSV into MoneyManagementEX (use the speedy method above)
2. Export as QIF
3. Import into HomeBank
   * HomeBank has their own CSV format, but MMEX can handle arbitrary CSV formats.

## stmt2csv.py

### Requirements

* Python 3.8
* pipenv

### Process

* git clone git@github.com:jeremysquires/bankstate.git
* cd bankstate
* pipenv install --dev
* pipenv shell
* Prepare input text using the correct `Text Copy` procedure
* python stmt2csv.py bankstatement.txt > output.csv
* Open CSV in LibreOffice/Excel to verify it has the correct structure
* Import Into Budgeting Software

### BMO MC Statement Text Copy

Input Data Format:

* The first line of the file gives the column headers for the CSV
* ASSUMES column header values do not contain spaces themselves
* Blank lines separate sections
  * EXCEPT no blank line between the header and the first section
* Each section corresponds to one column in the target CSV
* A group of sections corresponding to the column headers is called a block
* Credit card entries reverse the sign for amounts, credits are negative
* Checking entries have the expected sign for amounts, debits are negative
* Amounts use period (.) for the decimal separator
* Dollar signs ($) and thousands separators (,) are ignored

Algorithm:

* For each section, read lines into a list of values associated with a column
* Each subsequent section goes into the next column list until the last
* Convert dates from Mon Day YYYY to YYYY-MM-DD
* Clean up dollar values, sign of credits and other punctuation inconsistencies

Manual Data Manipulation:

* Paste header into empty file
  * TRANSDATE POSTINGDATE PAYEE REFERENCENO AMOUNT
* Open PDF in Evince or Okular
  * Acrobat Reader does not work because of restricted permissions to copy
* Copy each column one at a time into a separate section in the file
* If the file is protected by DRM, use Okular to export to text

Example copied text:

```
Jan. 15
Jan. 15

Jan. 16
Jan. 16

CO-OP GROCERY TOWN
IO
HOME STAR DINER
TOWN
IO

800178830919
800129277947

108.64
44.93
```

* If a value ends in CR, then it is a credit (remove CR, set sign to negative)
* Values that have a comma in them should have them removed
* Bring the Payee entries onto a single line

```
CO-OP GROCERY TOWN IO
HOME STAR DINER TOWN IO
```

Occasionally payees/reference numbers will get mixed up .. fix these

Add YYYY to the end of the dates

```
Jan. 15 2017
Jan. 15 2017

Jan. 16 2017
Jan. 16 2017
```

Assume:

* Each section has the same number of values as all other sections in block

### BMO Checking Statement Text Copy

Are similar to BMO MC Statements, only they only have 3 columns

Date Payee Amount

Similar manual fixes have to be implemented and the BMO MC code should work

### RBC MC Statement Text Copy

* The first line of the file gives the column headers for the CSV
* Assumes column header values do not contain tabs themselves
* Each line has an entire record, tab separated
* Dates are in MON DD YYYY format
* Currency is in -$1,111.11 format

Algorithm:

* Convert dates to YYYY-MM-DD
* Convert currency to -1111.11 format
* Convert tabs to commas, if a comma is in the field, add double quotes

Manual Data Manipulation:

* Use Adobe Acrobat Reader
* Paste header into empty file (note tab separation)
  * TRANSDATE	POSTINGDATE	PAYEE	REFERENCENO	AMOUNT
* Copy all lines in a block of text into the file

Example:

```
AUG 10 AUG 11 RIVER NATURAL PARK TOWN IO
55134426223800174862247
$37.66
AUG 12 AUG 15 AIRLINE 883826008065855 TOWN IO
55503806227004023214302
$36.75
```

* Change spaces to tabs
* Add YYYY to dates
* Occasionally, a reference number will need to be added - add any number 0000

```
AUG 10 2016	AUG 11 2016	RIVER NATURAL PARK TOWN IO	55134426223800174862247	$37.66
AUG 12 2016	AUG 15 2016	AIRLINE 883826008065855 TOWN IO	55503806227004023214302	$36.75
```

## Tests

There are unit tests for the utils that can be run with `pipenv run test`.
Testing the handlers requires some PDF data samples.
Once the PDF Data Samples are set up, you can run `pipenv run test_<statement_type>`.
See Pipfile for the list of tests available under the `scripts` section.

### PDF Data Samples

In the `test/data` folder, add the following PDF files from samples you download (they won't be added to the repo because of a .gitignore on the `test/data` folder):

* bmo_bank.pdf
* bmo_card.pdf
* bmo_card2.pdf
* rbc_bank.pdf
* rbc_bank2.pdf
* rbc_bank_2023.pdf
* rbc_card.pdf

### Automate Tests

If you have a `bash` interpreter installed, you can run the tests and comparisons all in one.

* `cd test`
* `bash test_handlers.sh`

The `test/data/orig` and `test/data/new` folders will be created by the `test_handlers.sh` script.
The first time it runs it will populate the `orig` folder with the `.tsv` files.
Every subsequent run, the `new` folder will be populated and compared with the `orig` using `diff`.

## Debug

The debug setup uses VSCode.
Debug scenarios are set up in `.vscode/launch.json`
In VSCode, open the `Run and Debug` side panel (the bug and triangle icon)
Open the `pdf2txt.py` python script in an editor window.
Pull down the dropdown to the right of the Green Debug triangle at the top of the panel.
Select the test you want to debug.
