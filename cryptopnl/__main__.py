import sys
from cryptopnl.main.profits_calculator import profitsCalculator 

def main(trades_file, ledger_file = None):
    return  profitsCalculator(trades_file=trades_file, ledger_file=ledger_file).go()

if __name__ == "__main__":
    sys.exit(
        main(*sys.argv[1:])
    )

# TODO RESULT : where are the decimals coming from !