bankstate
=========

Bank Statement Conversion for Import Into Home Finance Software

Scripts
-------

stmt2csv.py

Converts text copied from bank statements in PDF format into a CSV format that can be imported into home finance software

Copyright (C) 2017 Jeremy Squires <jms@mailforce.net>

License: https://opensource.org/licenses/MIT

When doing a first budget, the first step is invariably to collect at least a year's worth of data to form a reliable basis for the budget.  Unfortunately, few banking institutions provide more than a few months of data in any of the download formats supported by home finance software.  The first time budgeter is forced to download PDF statements from their accounts and somehow convert them for import into their home finance software.  At least one of the commercial finance packages provide OCR of scanned statements (Quicken), but none of the free ones that I checked (HomeBank, GnuCash, MoneyManagementEX).  In any case, the PDF files allow extraction of the text data without having to OCR them, so this is the preffered method.  The data that is copy/pasted from PDFs is not in any format that can be imported, so this is what this software provides.

Generated CSV files follow the following convention:
	https://tools.ietf.org/html/rfc4180 CSV RFC

Process
-------

### BMO MC Statements ###

Input Data Format:

* The first line of the file gives the column headers for the CSV
* ASSUMES column header values do not contain spaces themselves
* Blank lines separate sections
  - EXCEPT no blank line between the header and the first section
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
  - TRANSDATE POSTINGDATE PAYEE REFERENCENO AMOUNT
* Open PDF in Evince
  - Acrobat Reader does not work because of restricted permissions to copy
* Copy each column one at a time into a separate section in the file

Example:

> Jan. 15
> Jan. 15
> 
> Jan. 16
> Jan. 16
> 
> CO-OP GROCERY TOWN
> IO
> HOME STAR DINER
> TOWN
> IO
> 
> 800178830919
> 800129277947
> 
> 108.64
> 44.93

* If a value ends in CR, then it is a credit (remove CR, set sign to negative)
* Values that have a comma in them should have them removed
* Bring the Payee entries onto a single line

> CO-OP GROCERY TOWN IO
> HOME STAR DINER TOWN IO

Occasionally payees/reference numbers will get mixed up .. fix these

Add YYYY to the end of the dates

> Jan. 15 2017
> Jan. 15 2017
> 
> Jan. 16 2017
> Jan. 16 2017

Assume:

* Each section has the same number of values as all other sections in block

### BMO Checking Statements ###

Are similar to BMO MC Statements, only they only have 3 columns

Date Payee Amount

Similar manual fixes have to be implemented and the BMO MC code should work

### RBC MC Statements ###

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
  - TRANSDATE	POSTINGDATE	PAYEE	REFERENCENO	AMOUNT
* Copy all lines in a block of text into the file

Example:

> AUG 10 AUG 11 RIVER NATURAL PARK TOWN IO
> 55134426223800174862247
> $37.66
> AUG 12 AUG 15 AIRLINE 883826008065855 TOWN IO
> 55503806227004023214302
> $36.75

* Change spaces to tabs
* Add YYYY to dates
* Occasionally, a reference number will need to be added - add any number 0000

> AUG 10 2016	AUG 11 2016	RIVER NATURAL PARK TOWN IO	55134426223800174862247	$37.66
> AUG 12 2016	AUG 15 2016	AIRLINE 883826008065855 TOWN IO	55503806227004023214302	$36.75

Import
------

For financial packages with flexible CSV import (MoneyManagementEX, GnuCash):

Open the file and use the CSV header column mapping feature to set, at a minimum, map the following columns:

* Date
* Payee
* Amount
  - Some statements have Deposit and Withdrawal instead of Amount

All the other fields can be mapped to "Don't Care"

For HomeBank users: 

Import resulting CSVs into MoneyManagementEX, export as QIF, then import into HomeBank as HomeBank has their own CSV format, but MMEX can handle arbitrary CSV formats.  Not sure about GnuCash/GnuAccounting/Quicken/QuickBooks ...


