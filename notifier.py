import robin_stocks as rs
import os, sys, time, requests, json

with open(os.path.join(sys.path[0], 'login.txt')) as f:
    username = f.readline().strip()
    password = f.readline().strip()
    token = f.readline().strip()
    
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
        
        return -1

    def getProfits(self):
        totalProfit = 0
        for symbol in self.cryptoDict:
            totalProfit += self.getProfit(symbol)
        
        return totalProfit
    
    def calcBuyAvg(self, symbol, perPrice, quantity):
        if symbol in self.cryptoDict:
            quant = self.cryptoDict[symbol]['quantity'] + quantity
            cst = self.cryptoDict[symbol]['cost'] + (perPrice * quantity)
            return cst/quant

        return -1
    
    def calcProfit(self, buyPerPrice, buyAmt, sellPerPrice, sellAmnt):
        return (sellPerPrice * sellAmnt) - (buyPerPrice * buyAmt)

    def calcPosProf(self, symbol, perPrice):
        if symbol in self.cryptoDict:
           buySellAmnt = self.cryptoDict[symbol]['quantity']
           buyPerPrice = self.cryptoDict[symbol]['cost']/ self.cryptoDict[symbol]['quantity']
           return self.calcProfit(buyPerPrice, buySellAmnt, perPrice, buySellAmnt)
        
        return -1

def pushbullet_message(title, body, token):
    msg = {"type": "note", "title": title, "body": body}
    resp = requests.post('https://api.pushbullet.com/v2/pushes', 
                         data=json.dumps(msg),
                         headers={'Authorization': 'Bearer ' + token,
                                  'Content-Type': 'application/json'})
    if resp.status_code != 200:
        raise Exception('Error', resp.status_code)
    else:
        print ('Sent: {} - {}'.format(title, body)) 

if __name__ == "__main__":
    while True:
        expireTime = 86400
        rs.login(username= username, password= password, expiresIn= expireTime, by_sms=True)
        now = time.perf_counter()
        symb = 'DOGE'
        print(symb)
        while True:
            mc = myCryptos()
            p = mc.getProfit(symb)
            pp = mc.getPercProf(symb)
            notifAmnt = 10
            msg = 'profit at $ {:.3f} ({:.3f}%)'.format(p, pp*100)
            
            print(msg, end='\r')
            
            if p >= notifAmnt:
                pushbullet_message(symb, msg, token)
                notifAmnt = p + 10
            if p > 0 and (notifAmnt - p) > 10: 
                notifAmnt = p + 10
        
            if p < 0: notifAmnt = 10

            #Check for time
            timePass = time.perf_counter() - now
            if timePass >= expireTime: break
            time.sleep(1)

        rs.logout()