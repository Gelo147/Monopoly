from Space import Space
class TaxSpace(Space):
    def __init__(self,text,fee):
        super().__init__("TAX",text)
        self._fee = fee
        
    def __str__(self):
        return "[%s // %s]\n" % (self._text,str(self._fee)+'€')
    def getFee(self):
        return self._fee
