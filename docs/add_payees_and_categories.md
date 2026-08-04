# Payees and Categories

The recommended process is to load the CSV/TSV data once, mapping the Description column to Payee, then to delete all transactions, map categories to all payees, then reimport, so that categories will be assigned as a consequence of the payee.

The problem with this approach is that most descriptions that have payee information also include account numbers, locations, and other data that means you end up with a lot of duplicate payees. When loading a large amount of data, this can become unwieldy.

## Examples

All the following should be Payee: `MAGOO'S`, `ONLINESTORE CA`, `ONLINESTORE`, `SHOPNAME`, `OTHERSHOP`, `BOOKSTORE`

```text
MAGOO'S #5079
MAGOO'S #7135
MAGOO'S #9617
ONLINESTORE CA*JF88888 WWW.STORE.COM
ONLINESTORE CA*B63AC99 WWW.STORE.COM
ONLINESTORE 12345678 WWW.STORE.COM
#930 SHOPNAME CITY1 PROVINCE1
#920 SHOPNAME CITY2 PROVINCE2
OUTER ROAD OTHERSHOP CITY1 PROVINCE1
INNER ROAD OTHERSHOP CITY1 PROVINCE1
BOOKSTORE 123 CITY1
BOOKSTORE 999 CITY2
etc.
```

All the following should not include the category of transaction prefix in the Payee name:

```text
INTERAC e-Transfer Sent Neighborhood Lawn Care
Online Bill Payment, POWER COMPANY
Direct Deposit, JOB INC. PAY/PAY
```

## Plan

* merge csvs: take a list of csvs and merge them into a single file with a single header for input
  * use duckdb - load_csvs with wildcard, potential transform to common header, then export
  * can use bash script as well - just omit all but the first header and cat all the rest of the files
* extract payees: read csvs into tables, select the description column, process regex to give payee info only, save to new csvs
  * use duckdb - using duckdb ui, craft the SQL, save it to file, then develop a duckdb SQL driver in Python to automate
* create payees and categories: given a specific payee, apply a category
  * prepare a fake import csv with the final payees and associated categories
  * import the fake import
  * add the regexes to pattern match payees on import (mmex feature)
  * remove all the fake transations
  * save as a template db
* merge payees: if duplicate payees exist, then merge them
  * mmex provides an import feature where regexes for payees will force them to be merged
  * mmex provides a UI to merge payees after import
  * alternatively: use dbeaver/duckdb to craft SQL to merge them (duckdb does not read mmex mmdb correctly)
