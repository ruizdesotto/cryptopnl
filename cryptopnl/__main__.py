from cryptopnl.calc.cump import doCumpCalculation

if __name__ == "__main__":
    #sys.exit(sys.args) or smth like that
    doCumpCalculation(".env/ledgers.csv", 
                      ".env/trades.csv", 
                      ".env/prices4cump.json")