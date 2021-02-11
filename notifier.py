import robin_stocks as rs
import os, sys, time

with open(os.path.join(sys.path[0], 'login.txt')) as f:
    username = f.readline().strip()
    password = f.readline().strip()
    
class myCryptos():
    def __init__(self):
        self.myCryptos = rs.crypto.get_crypto_positions()
        self.cryptoDict = self.buildCryptoDict()
    
    def buildCryptoDict(self):
        cryptoDict = {}
        for crypto in self.myCryptos:
            name = crypto['currency']['code']
            cost = float(crypto['cost_bases'][0]['direct_cost_basis'])
            quantity = float(crypto['cost_bases'][0]['direct_quantity'])
            cryptoDict[name] = {'cost': cost, 'quantity': quantity}
        
        return cryptoDict
    
    def getAvgPrice(self, symbol):
        if symbol in self.cryptoDict:
            if self.cryptoDict[symbol]['quantity'] != 0:
                return self.cryptoDict[symbol]['cost'] / self.cryptoDict[symbol]['quantity']
            
            return 0        
        return -1
    
    def getCurPrice(self, symbol):
        return float(rs.crypto.get_crypto_quote(symbol, info = 'mark_price'))

    def getProfit(self, symbol):
        if symbol in self.cryptoDict:
            price = self.getCurPrice(symbol)
            return (price * self.cryptoDict[symbol]['quantity']) - self.cryptoDict[symbol]['cost'] 

        return -1

    def getPercProf(self, symbol):
        if symbol in self.cryptoDict:
            price = self.getCurPrice(symbol)
            cost = self.cryptoDict[symbol]['cost']
            quantity = self.cryptoDict[symbol]['quantity']
            return  ((price * quantity) - cost)/cost

    def getProfits(self):
        totalProfit = 0
        for symbol in self.cryptoDict:
            totalProfit += self.getProfit(symbol)
        
        return totalProfit

while True:
    expireTime = 86400
    rs.login(username= username, password= password, expiresIn= expireTime, by_sms=True)
    now = time.perf_counter()
    while True:
        mc = myCryptos()
        p = mc.getProfit('DOGE')
        pp = mc.getPercProf('DOGE')
        print(round(p,4))
        timePass = time.perf_counter() - now
        if timePass >= expireTime: break
        time.sleep(1)

    rs.logout()


#tick = yf.Ticker('DOGE-USD')
#print(tick.info['regularMarketPrice'])