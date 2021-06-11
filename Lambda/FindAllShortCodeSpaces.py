from . import JDTools

entries, codes = JDTools.get_current_danzi_codes()

for s in sorted('qwfpgjluy;rstdhnzxcbkm'):
    for y in sorted('qwfpgjluy;rstdhnzxcbkm'):
        if s+y not in codes:
            print(s+y)
