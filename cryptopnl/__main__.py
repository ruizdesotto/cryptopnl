import sys
from cryptopnl.main.profits_calculator import profitsCalculator 

def main(trades_file, ledger_file = None):
    calc =  profitsCalculator(trades_file=trades_file, ledger_file=ledger_file)
    return calc.go()

if __name__ == "__main__":
    sys.exit(
        main(*sys.argv[1:])
    )