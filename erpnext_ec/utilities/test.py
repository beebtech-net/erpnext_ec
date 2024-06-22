from doc_builder_tools import *
from datetime import date

res1 = GenerarClaveAcceso('01',date(2024, 4, 20),'001','133','1','0993371265001','2','001')
print("esperado 2004202401099337126500120010020000001331234567814")
print(res1)

res2 = GenerarClaveAcceso('01',date(2024, 12, 6),'001','143','1','0993371265001','2','001')
print ("esperado 1106202401099337126500120010020000001431234567812")
print(res2)
