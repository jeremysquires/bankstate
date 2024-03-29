CWD=$(pwd)
if [ -f ../pdf2txt.py ]; then
  cd ..
fi
pipenv run test_bmo_bank
pipenv run test_bmo_card
pipenv run test_bmo_card2
pipenv run test_rbc_bank
pipenv run test_rbc_bank2
pipenv run test_rbc_bank_2023
pipenv run test_rbc_card

# check test output
cd test/data
if [ -d ./new ]; then
  rm -Rf ./new
fi
if [ -d ./orig ]; then
  mkdir ./new
  mv *.tsv ./new
  diff orig new
else
  mkdir ./orig
  mv *.tsv ./orig
fi

cd $CWD

