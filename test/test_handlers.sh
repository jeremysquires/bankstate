# test_handlers.sh - test various command line parameters on private data that is not in the repo (yet)
#
# data structure (NOTE: test/data is gitignored so PII is not uploaded to git):
#   input from data/input
#   output to data/new
#   captures to data/raw
#   validated output in data/orig
#
# First run:
#   All the newly created outputs will be copied automatically to the data/orig folder
#   WARN: You need to check all of these by hand, ensuring that they are correct, otherwise
#   the next time you run the tests, they will all be reported green, whether they are good or not.
#   Remove any incorrect output from the orig folder.
#
# Fix runs:
#   Each time you make changes and fix the output in new, check it for correctness.
#   If the new output is correct, copy it to the data/orig folder for new runs to check regression.
#
# Add new test:
#   1. run a new command line in this script
#   2. the diff will identify any files not already in data/orig
#   3. check the output in data/new, and if correct, copy it to data/orig

CWD=$(pwd)

if [ -f ../pdf2txt.py ]; then
  cd ..
  if [ -d ./test/data/new ]; then
    rm -Rf ./test/data/new
  fi
fi
mkdir -p ./test/data/new

# test_bmo_bank
pipenv run python pdf2txt.py ./test/data/input/bmo_bank.pdf bmo_bank ./test/data/new/bmo_bank.tsv -c ./test/data/raw/bmo_bank.txt
# test_bmo_card
pipenv run python pdf2txt.py ./test/data/input/bmo_card.pdf bmo_card ./test/data/new/bmo_card.tsv -c ./test/data/raw/bmo_card.txt
# test_bmo_card2
pipenv run python pdf2txt.py ./test/data/input/bmo_card2.pdf bmo_card ./test/data/new/bmo_card2.tsv -c ./test/data/raw/bmo_card2.txt
# test_rbc_bank
pipenv run python pdf2txt.py ./test/data/input/rbc_bank.pdf rbc_bank ./test/data/new/rbc_bank.tsv -c ./test/data/raw/rbc_bank.txt
# test_rbc_bank2
pipenv run python pdf2txt.py ./test/data/input/rbc_bank2.pdf rbc_bank ./test/data/new/rbc_bank2.tsv -c ./test/data/raw/rbc_bank2.txt
# test_rbc_bank_2023
pipenv run python pdf2txt.py ./test/data/input/rbc_bank_2023.pdf rbc_bank ./test/data/new/rbc_bank_2023.tsv -c ./test/data/raw/rbc_bank_2023.txt
# test_rbc_bank_2025
pipenv run python pdf2txt.py ./test/data/input/rbc_bank_2025.pdf rbc_bank ./test/data/new/rbc_bank_2025.tsv -c ./test/data/raw/rbc_bank_2025.txt
# test_rbc_card
pipenv run python pdf2txt.py ./test/data/input/rbc_card.pdf rbc_card ./test/data/new/rbc_card.tsv -c ./test/data/raw/rbc_card.txt
# test_rbc_card_2026
pipenv run python pdf2txt.py ./test/data/input/rbc_card_2026.pdf rbc_card ./test/data/new/rbc_card_2026.tsv -c ./test/data/raw/rbc_card_2026.txt

# check test output
cd test/data
if [ -d ./orig ]; then
  diff orig new
else
  mkdir ./orig
  cp ./new/*.tsv ./orig
fi

# check processing raw input test_bmo_bank will result in the same output (don't need to check all of them)
cd ../..
pipenv run python pdf2txt.py ./test/data/raw/bmo_bank.txt bmo_bank ./test/data/new/bmo_bank.tsv -f cap
cd test/data
diff orig new

cd $CWD
