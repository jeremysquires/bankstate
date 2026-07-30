CWD=$(pwd)

if [ -f ../pdf2txt.py ]; then
  cd ..
  if [ -d ./test/data/new ]; then
    rm -Rf ./test/data/new
  fi
fi
mkdir -p ./test/data/new

pipenv run test_bmo_bank
pipenv run test_bmo_card
pipenv run test_bmo_card2
pipenv run test_rbc_bank
pipenv run test_rbc_bank2
pipenv run test_rbc_bank_2023
pipenv run test_rbc_bank_2025
pipenv run test_rbc_card
pipenv run test_rbc_card_2026

# check test output
cd test/data
if [ -d ./orig ]; then
  diff orig new
else
  mkdir ./orig
  cp ./new/*.tsv ./orig
fi

cd $CWD
