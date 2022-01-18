class Logger:
    def __init__(self):
        self.trades = []
    
    def logTrade(self, outing, ining):
        line  = "========================================\n"
        c = -outing.amount+outing.fee if outing.asset.endswith("EUR") else "" 
        line += f"--- {outing.asset} {outing.amount} (-{outing.fee})\t\t {c}\n" 
        line += f"+++ {ining.asset} {ining.amount} (-{ining.fee})\n"
        self.trades.append(line)
    
    def logWallet(self, value, wallet):
        self.trades.append(f"Cost: {wallet.getCost()} \tValue: {value}\n")
        bal = ""
        for c in wallet.amounts.keys():
            bal += f"{c} :\t {wallet.amounts[c]}\n"
        self.trades.append(bal)

    def getTrades(self):
        return "\n".join(self.trades)
    
    def save(self):
        with open("logging.txt", "w") as file1:
            file1.writelines(self.trades)