import slate3k as slate
text  = slate.PDF(open('./data/bmo_chq_eStatement_2022-11-04.pdf', 'rb')).text()
print(text)

# NADA