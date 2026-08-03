# bankstate

Bank Statement Conversion for Import Into Home Finance Software

When doing a budget, the first step is invariably to collect at least a year's worth of data to form a reliable basis for the budget. Unfortunately, few banking institutions provide more than a few months of data in any of the download formats supported by home finance software. The first time budgeter is forced to download PDF statements from their accounts and somehow convert them for import into their home finance software. At least one of the commercial finance packages provide OCR of scanned statements (Quicken), but none of the free ones that I checked (HomeBank, GnuCash, MoneyManagementEX). In any case, the PDF files allow extraction of the text data without having to OCR them, so this is the preferred method.

## License

Copyright (C) 2017, 2023, 2026 Jeremy Squires <jms@mailforce.net>

License: <https://opensource.org/licenses/MIT>

## Scripts

pdf2txt.py

Reads PDF bank and mastercard statements and directly outputs a CSV format that can be imported into home finance software

The stmt2csv.py script has been removed, but there is an option to import raw text capture files `--format cap` instead of PDFs, so it is possible to create the input files from any source by copying and pasting or exporting the text and manipulating it to fit one of the capture formats.

## Supported Data Formats

* Bank of Montreal (BMO) bank account and credit card statements in PDF format
* Royal Bank of Canada (RBC) bank account and credit card statements in PDF format

Generated CSV files follow the CSV RFC: <https://tools.ietf.org/html/rfc4180> and contain columns that in general match the input files, but with some cleanups to make import easier. Generated TSV files replace commas for tabs, which is useful when fields often contain commas.

## pdf2txt.py

### Requirements

* Python 3.9
* pipenv

### Process

```bash
git clone git@github.com:jeremysquires/bankstate.git
cd bankstate
pipenv install --dev
pipenv shell
python pdf2txt.py filename.pdf <filetype> output.tsv
# Where: filetype = [ bmo_bank | bmo_card | rbc_bank | rbc_card ]
```

* Open TSV in LibreOffice/Excel to verify it has the correct structure
* Import Into Budgeting Software

### Capture Export Text for Debug

Add the parameter `--capture <capture_filepath>` or `-c <capture_filepath>` to save the raw text exported from the PDF to a file.

This file can be more easily examined than the PDF to determine whether the problem was in the PDF export or in the text parser.

These captured exports can also be sanitized or anonymized to remove any personally identifiable information in case they need to be reproduced or debugged by someone other than the owner of the data.

In order to test changes to the raw text itself, add the parameter `--format cap` and pass the path to the raw text capture file in as the input filename rather than a PDF.

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

## Tests

* There are unit tests for the utils that can be run with `pipenv run test`.
* Testing the handlers requires some PDF data samples.
* Once the PDF Data Samples are set up, you can run `pipenv run test_handlers`.
* See the `test/test_handlers.sh` script for the list of tests available under the `scripts` section.

### PDF Data Samples

In the `test/data/input` folder, add the following PDF files from samples you download

(NOTE: none of the test data will be added to the repo because of a `.gitignore` on the `test/data` folder):

* bmo_bank.pdf
* bmo_card.pdf
* bmo_card2.pdf
* rbc_bank.pdf
* rbc_bank2.pdf
* rbc_bank_2023.pdf
* rbc_card.pdf

### Automate Tests

If you have a `bash` interpreter installed, you can run the tests and comparisons all in one.

```bash
cd test
bash test_handlers.sh
```

### Data structure

(NOTE: `test/data` is gitignored so PII is not uploaded to git):

* input PDFs from `data/input`
* output TSVs to `data/new`
* capture TXTs to `data/raw`
* validated TSV output in `data/orig`

### First Run

* All the newly created outputs will be copied automatically to the `data/orig` folder
  * WARN: You need to check all of these by hand, ensuring that they are correct, otherwise the next time you run the tests, they will all be reported green, whether they are good or not.
* Remove any incorrect output from the orig folder.

### Debug Runs

* Each time you make changes and fix the output in new, check it for correctness.
* If the new output is correct, copy it to the data/orig folder for new runs to check regression.

### Add New Test

1. Add a new command line to the `test_handlers.sh` script and run it
2. The diff output will identify any files not already in `data/orig`
3. Check the output in `data/new`, and if correct, copy it to `data/orig`

## Debug Unit Tests

* The debug setup uses VSCode.
* Debug scenarios are set up in `.vscode/launch.json`
* In VSCode, open the `Run and Debug` side panel (the bug and triangle icon)
* Open the `pdf2txt.py` python script in an editor window.
* Pull down the dropdown to the right of the Green Debug triangle at the top of the panel.
* Select the test you want to debug.
