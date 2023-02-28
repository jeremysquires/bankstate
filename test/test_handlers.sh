CWD=$(pwd)
if [ -f ../pdf2txt.py ]; then
  cd ..
fi
pipenv run test_bmo_bank
pipenv run test_bmo_card
pipenv run test_bmo_card2
pipenv run test_rbc_bank
pipenv run test_rbc_bank2
pipenv run test_rbc_card
cd $CWD