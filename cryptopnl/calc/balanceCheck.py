from decimal import Decimal as D

def checkBalanceWithFees(ledger):
    bal = {"ZEUR": D(0), "XXBT": D(0), "XETH": D(0), "XLTC": D(0)}
    ledgerBal = {"ZEUR": D(0), "XXBT": D(0), "XETH": D(0), "XLTC": D(0)}
    for _, row in ledger.iterrows():
        if type(row.txid) == str and row.txid:
            bal[row.asset] += D(str(row.amount)) - D(str(row.fee))
            ledgerBal[row.asset] = D(str(row.balance))
        
    return (bal, ledgerBal)