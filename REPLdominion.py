import random
from collections import Counter, OrderedDict
from operator import itemgetter
import re
import pandas

class Card():
    def __init__(self,name,category,cost,buypower,vpoints):
        self.name = name
        self.category = category
        self.cost = cost
        self.buypower = buypower
        self.vpoints = vpoints
    def react(self,player):
        return False

class Coin_card(Card):
    def __init__(self,name,cost,buypower):
        Card.__init__(self,name,"coin",cost,buypower,0)

class Copper(Coin_card):
    def __init__(self):
        Coin_card.__init__(self,"Copper",0,1)
        
class Silver(Coin_card):
    def __init__(self):
        Coin_card.__init__(self,"Silver",3,2)
        
class Gold(Coin_card):
    def __init__(self):
        Coin_card.__init__(self,"Gold",6,3)

class Victory_card(Card):
    def __init__(self,name,cost,vpoints):
        Card.__init__(self,name,"victory",cost,0,vpoints)

class Estate(Victory_card):
    def __init__(self):
        Victory_card.__init__(self,"Estate",2,1)
        
class Duchy(Victory_card):
    def __init__(self):
        Victory_card.__init__(self,"Duchy",5,3)
    
class Province(Victory_card):
    def __init__(self):
        Victory_card.__init__(self,"Province",8,6)

class Garden(Victory_card):
    def __init__(self):
        Victory_card.__init__(self,"Garden",4,0)

class Curse(Card):
    def __init__(self):
        Card.__init__(self,"Curse","curse",0,0,-1)

class Action_card(Card):
    def __init__(self,name,cost,actions,cards,buys,coins):
        Card.__init__(self,name,"action",cost,0,0)
        self.actions = actions
        self.cards = cards
        self.buys = buys
        self.coins = coins
    def use(self,player,trash):
        player.played.append(self)
        player.hand.remove(self)
    def augment(self,player):
        player.actions+=self.actions
        player.buys+=self.buys
        player.purse+=self.coins
        for i in range(self.cards):
            player.draw()
    def play(self,player,players,supply,trash):
        pass
    
class Woodcutter(Action_card):
    def __init__(self):
        Action_card.__init__(self,"Woodcutter",3,0,0,1,2)

class Smithy(Action_card):
    def __init__(self):
        Action_card.__init__(self,"Smithy",4,0,3,0,0)

class Laboratory(Action_card):
    def __init__(self):
        Action_card.__init__(self,"Laboratory",5,1,2,0,0)

class Village(Action_card):
    def __init__(self):
        Action_card.__init__(self,"Village",3,2,1,0,0)

class Festival(Action_card):
    def __init__(self):
        Action_card.__init__(self,"Festival",5,2,0,1,2)

class Market(Action_card):
    def __init__(self):
        Action_card.__init__(self,"Market",5,1,1,1,1)

class Chancellor(Action_card):
    def __init__(self):
        Action_card.__init__(self,"Chancellor",3,0,0,0,2)
    def play(self,player,players,supply,trash):
        if player.yesnoinput('Would you like to discard your entire deck?'):
            player.discard = player.discard + player.deck
            player.deck = []

class Workshop(Action_card):
    def __init__(self):
        Action_card.__init__(self,"Workshop",3,0,0,0,0)
    def play(self,player,players,supply,trash):
        player.gaincard(supply,4)

class Moneylender(Action_card):
    def __init__(self):
        Action_card.__init__(self,"Moneylender",4,0,0,0,0)
    def play(self,player,players,supply,trash):
        c = getcard("Copper",supply,player.hand,"your hand")        
        if c:
            trash.append(c)
            player.hand.remove(c)
            player.purse += 3

class Chapel(Action_card):
    def __init__(self):
        Action_card.__init__(self,"Chapel",2,0,0,0,0)
    def play(self,player,players,supply,trash):
        trashed=0        
        while trashed<4 and len(player.hand)>0:
            trashcard = input("Choose a card from your hand to trash: ")
            if not trashcard:
                break
            c = getcard(trashcard,supply,player.hand,"your hand")
            if c:
                trash.append(c)
                player.hand.remove(c)
                trashed+=1

class Cellar(Action_card):
    def __init__(self):
        Action_card.__init__(self,"Cellar",2,1,0,0,0)
    def play(self,player,players,supply,trash):
        discarded=0        
        while len(player.hand)>0:
            dis_card=input("Choose a card from your hand to discard: ")
            if not dis_card:
                break
            c = getcard(dis_card,supply,player.hand,"your hand")
            if c:
                player.discard.append(c)
                player.hand.remove(c)
                discarded+=1
        for j in range(discarded):
            player.draw()

class Remodel(Action_card):
    def __init__(self):
        Action_card.__init__(self,"Remodel",4,0,0,0,0)
    def play(self,player,players,supply,trash):
        while len(player.hand)>0:
            this_card = input("Choose a card from your hand to remodel: ")
            c = getcard(this_card,supply,player.hand,"your hand")
            if c:
                trash.append(c)
                player.hand.remove(c)
                player.gaincard(supply,c.cost+2)
                break

class Adventurer(Action_card):
    def __init__(self):
        Action_card.__init__(self,"Adventurer",6,0,0,0,0)
    def play(self,player,players,supply,trash):
        coins_added = 0
        while (player.deck or player.discard) and coins_added <2:
            player.draw()
            if player.hand[-1].category == "coin":
                coins_added +=1
            else:
                player.aside.append(player.hand.pop())

class Feast(Action_card):
    def __init__(self):
        Action_card.__init__(self,"Feast",4,0,0,0,0)
    def use(self,player,trash):
        trash.append(self)
        player.hand.remove(self)
    def play(self,player,players,supply,trash):
        player.gaincard(supply,5)

class Mine(Action_card):
    def __init__(self):
        Action_card.__init__(self,"Mine",5,0,0,0,0)
    def play(self,player,players,supply,trash):
        while "coin" in catinlist(player.hand):
            this_card = input("Choose a coin from your hand to upgrade: ")
            c = getcard(this_card,supply,player.hand,"your hand",["coin"])
            if c:
                trash.append(c)
                player.hand.remove(c)
                while c.cost>2 or len(supply["Copper"])>0 or len(supply["Silver"])>0:
                    pick = input("Choose a coin to gain.  Any coin up to " + str(c.cost+3)+": ")
                    g = getcard(pick,supply,categories=["coin"],upto=c.cost+3)
                    if g:
                        player.hand.append(g)
                        supply[pick].remove(g)
                        break
                break

class Library(Action_card):
    def __init__(self):
        Action_card.__init__(self,"Library",5,0,0,0,0)
    def play(self,player,players,supply,trash):
        while (player.deck or player.discard) and len(player.hand) <7:
            player.draw(player.hold)
            if (player.hold[-1].category == "action" and not player.yesnoinput("You drew " + player.hold[-1].name + ".  Would you like to keep it?",", add to my hand", ", set it aside")):
                player.aside.append(player.hold.pop())
            else:
                player.hand.append(player.hold.pop())

class Moat(Action_card):
    def __init__(self):
        Action_card.__init__(self,"Moat",2,0,2,0,0)
    def react(self,player):
        player.show()        
        return player.yesnoinput(player.name + ", you have a " + self.name +
                        " in your hand.  Do you want to block the attack?")

class Council_Room(Action_card):
    def __init__(self):
        Action_card.__init__(self,"Council Room",5,0,3,1,0)
    def play(self,this_player,players,supply,trash):
        for player in players:
            player.draw()

class Witch(Action_card):
    def __init__(self):
        Action_card.__init__(self,"Witch",5,0,2,0,0)
    def play(self,this_player,players,supply,trash):
        if len(supply["Curse"])>0:
            for player in players:
                if player==this_player:
                    pass
                else:
                    for c in player.hand:
                        if c.react(player):
                            break
                    else:
                        if len(supply["Curse"])>0:
                            player.discard.append(supply["Curse"].pop())

class Bureaucrat(Action_card):
    def __init__(self):
        Action_card.__init__(self,"Bureaucrat",4,0,0,0,0)
    def play(self,this_player,players,supply,trash):
        if len(supply["Silver"])>0:
            this_player.deck.insert(0,supply["Silver"].pop())
        for player in players:
            if (not player==this_player) and ("victory" in catinlist(player.hand)):
                for c in player.hand:
                    if c.react(player):
                        break
                else:
                    player.show()
                    while True:                        
                        putback = player.choose_discard(player.name + ", which victory card" +
                        " do you want to put on top of your deck?\n--> ")
                        c = getcard(putback,supply,player.hand,"your hand",["victory"])
                        if c:
                            player.hand.remove(c)
                            player.deck.insert(0,c)
                            break
                        
class Militia(Action_card):
    def __init__(self):
        Action_card.__init__(self,"Militia",4,0,0,0,2)
    def play(self,this_player,players,supply,trash):
        for player in players:
            if (not player==this_player) and len(player.hand)>3:
                for c in player.hand:
                    if c.react(player):
                        break
                else:
                    player.show()
                    while len(player.hand)>3:
                        dis_card=player.choose_discard(player.name + ", choose a card from your hand to discard: ")
                        if dis_card:
                            c = getcard(dis_card,supply,player.hand,"your hand")
                            if c:
                                player.hand.remove(c)
                                player.discard.append(c)
                            
class Spy(Action_card):
    def __init__(self):
        Action_card.__init__(self,"Spy",4,1,1,0,0)
    def play(self,this_player,players,supply,trash):
        for player in players:
            for c in player.hand:
                if c.react(player):
                    break
            else:
                b = player.draw([])
                if not b:
                        continue
                else:
                    print("The first card in the deck of " + player.name + " is " + b.name)
                    if this_player.yesnoinput(this_player.name + ", do you want " + player.name + " to discard this?",
                    ", discard",", keep"):
                        player.discard.append(b)
                    else:
                        player.deck.insert(0,b)
                #check logic of this structure

class Thief(Action_card):
    def __init__(self):
        Action_card.__init__(self,"Thief",4,0,0,0,0)
    def play(self,this_player,players,supply,trash):
        for player in players:
            if player == this_player:
                continue
            for c in player.hand:
                if c.react(player):
                    break
            else:
                for i in range(2):
                    player.draw(player.hold)
                print( player.name, namesinlist(player.hold))
                if "coin" in catinlist(player.hold):
                    while True:
                        burn = input("Which card would you like " + player.name + " to trash?\n-->")                
                        c = getcard(burn,supply,player.hold," the top 2 cards",["coin"])
                        if c:
                            player.hold.remove(c)
                            break
                    if this_player.yesnoinput("Do you want to steal it?",", it's mine!",", leave it in the trash."):
                        this_player.discard.append(c)
                    else:
                        trash.append(c)
                player.discard=player.discard+player.hold
                player.hold = []

class Throne_Room(Action_card):
    def __init__(self):
        Action_card.__init__(self,"Throne Room",4,0,0,0,0)
    def play(self,player,players,supply,trash):
        if "action" in catinlist(player.hand):
            while True:
                double = input("What card would you like to double?\n--> ")            
                c = getcard(double,supply,player.hand," your hand",["action"])
                if c:
                    c.use(player,trash)
                    c.augment(player)
                    c.play(player,players,supply,trash)
                    player.show()
                    c.augment(player)
                    c.play(player,players,supply,trash)
                    break

                
class Player():
    def __init__(self,name):
        self.name = name
        deal = [Copper()]*7 + [Estate()]*3
        random.shuffle(deal)
        self.hand = deal[:5]
        self.deck = deal[5:]
        self.played = []
        self.discard = []
        self.aside = []
        self.hold = []
        random.shuffle(self.deck)
        for i in range(5):
            self.draw
    def other(self):
        return self.played+self.discard+self.hold+self.aside
    def stack(self):
        return (self.deck + self.hand + self.played + self.discard + self.aside + self.hold)
    def draw(self,dest=None):
        #defualt destination is player's hand
        if dest==None:
            dest = self.hand
        #Replenish deck if necessary.
        if len(self.deck)==0:
            self.deck = self.discard
            self.discard = []
            random.shuffle(self.deck)
        #If deck has cards, add card to destination list
        if len(self.deck)>0:
            c = self.deck.pop(0)
            dest.append(c)
            return c
    def turn(self,players,supply,trash):
        self.show()
        self.actions = 1
        self.buys = 1
        self.purse = 0
        #action phase
        while self.actions>0 and 'action' in catinlist(self.hand):
            playthis = input("Which card would you like to play?  You have " +
            str(self.actions) + " action(s).  \n-Hit enter for no play. --> ")
            if playthis:
                c = getcard(playthis,supply,self.hand,"your hand",['action'])
                if c:
                    self.actions = self.actions - 1 
                    c.use(self,trash)
                    c.augment(self)
                    c.play(self,players,supply,trash)
                    self.show()
            else:
                self.actions=0
        #buy phase
        for c in self.hand:
            self.purse += c.buypower
        while self.buys>0:
            buy_string = "Buying power is " + str(self.purse) + ".  You have " + str(self.buys) + " buy"
            if self.buys>1:
                buy_string += "s"
            buy_string += "."
            print( buy_string)
            purchase = input("What would you like to purchase?  -Hit enter for no purchase.-\n--> ")
            if not purchase:
                break
            else:
                c = getcard(purchase,supply,upto=self.purse)
                if c:
                    self.discard.append(supply[purchase].pop())
                    self.buys = self.buys -1
                    self.purse = self.purse - c.cost
                    
        #cleanup phase
        self.discard = self.discard + self.played + self.hand + self.aside
        self.played = []
        self.hand = []
        self.aside = []
        for i in range(5):
            self.draw()

    def gaincard(self,supply,upto):
        while True:
            gain = input("What would you like to get?  Any card up to " + str(upto) + "\n--> ")
            c = getcard(gain,supply,upto=upto)
            if c:
                self.discard.append(c)
                supply[gain].remove(c)
                break
    def yesnoinput(self,prompt,yesstring='',nostring=''):
        print(prompt + "\n1 - Yes" + yesstring + "\n0 - No" + nostring)
        while True:
            r = input("--> ")        
            if r == "0":
                return False
            if r == "1":
                return True    
    
    def choose_discard(self,prompt):
        return input(prompt)

    def show(self):
        print (self.name)
        print ("hand:  ", namesinlist(self.hand))
        shuffled_deck = namesinlist(self.deck)
        random.shuffle(shuffled_deck)
        print ("deck (not in order):  ", shuffled_deck)
        print ("discard: ", namesinlist(self.discard))
        if len(self.played)>0:
            print ("played: ", namesinlist(self.played))
        if len(self.aside)>0:
            print ("aside: ",namesinlist(self.aside))
        print ("\r")
    
    def action_balance(self):
        balance = 0
        for c in self.stack():
            if c.category == "action":
                balance = balance - 1 + c.actions
        return 70*balance / len(self.stack())

    def cardsummary(self):
        summary = {}
        for c in self.stack():
            if c.name in summary:
                summary[c.name] += 1
            else:
                summary[c.name] = 1
        return summary

    def calcpoints(self):
        tally = 0
        gardens = 0
        n = 0
        for c in self.stack():
            tally += c.vpoints
            n += 1
            if c.name == "Garden":
                gardens+=1
        return tally + n//10 * gardens

class ComputerPlayer(Player):
    def __init__(self,name):
        Player.__init__(self,name)
        self.index = 0
        self.buygaintable = []
        #beginning and middle of game
        self.buygaintable1 = ["Province","Gold","Laboratory","Festival","Witch",
        "Council Room","Market","Militia","Adventurer","Smithy","Bureaucrat","Silver","Moat",""]
        #end of game        
        self.buygaintable2 = ["Province","Garden","Duchy","Estate","Gold","Silver",""]
        #beginning and middle of the game, too many action cards
        self.buygaintable3 = ["Province","Gold","Festival","Laboratory","Market","Village",
        "Silver",""]
        self.playtable1 = ["Village","Festival","Market","Laboratory","Witch",
        "Council Room","Militia","Adventurer","Smithy","Bureaucrat","Moat",""]
        self.discardtable1 = ["Garden","Duchy","Province","Estate","Curse","Copper",
        "Village","Bureaucrat","Silver","Militia","Smithy","Council Room","Witch",
        "Festival","Market","Adventurer","Laboratory","Gold","Moat"]
        
    def turn(self,players,supply,trash):
        self.show()
        self.actions = 1
        self.buys = 1
        self.purse = 0
        #action phase
        self.index = 0
        while self.actions>0 and 'action' in catinlist(self.hand):
            playthis = self.playtable1[self.index]
            if playthis:
                c = self.getcard(playthis,supply,self.hand,"your hand",['action'])
                if c:
                    #print (self.name + " plays " + c.name)
                    self.actions = self.actions - 1
                    c.use(self,trash)
                    self.index=0                    
                    c.augment(self)
                    c.play(self,players,supply,trash)
                    self.show()
                else:
                    self.index += 1
            else:
                self.actions=0
        #buy phase
        if len(supply["Province"])>len(players)+totalbuypower(self.deck)/8:
            if self.action_balance()<-10:
                self.buygaintable = self.buygaintable3
            else:
                self.buygaintable = self.buygaintable1
        else:
            self.buygaintable = self.buygaintable2
        self.index = 0
        for c in self.hand:
            self.purse += c.buypower
        while self.buys>0:
            purchase = self.buygaintable[self.index]
            if not purchase:
                break
            else:
                c = self.getcard(purchase,supply,upto=self.purse)
                if c:
                    self.discard.append(supply[purchase].pop())
                    self.index = 0
                    self.buys = self.buys -1
                    self.purse = self.purse - c.cost
                    #print (self.name + " bought " + c.name)
                else:
                    self.index += 1
                    
        #cleanup phase
        self.discard = self.discard + self.played + self.hand + self.aside
        self.played = []
        self.hand = []
        self.aside = []
        for i in range(5):
            self.draw()
    
    def getcard(self,name,supply,target_list=None,target_name= "the supply anymore",categories=['action','coin','curse','victory'],upto=100):
        if not name in supply:
            #print name + " is not in this game."
            return None
        if not target_list:
            target_list = supply[name]
        nameslist = namesinlist(target_list)
        if not name in nameslist:
            #print "There is no " + name + " in " + target_name
            return None
        i = nameslist.index(name)
        c = target_list[i]
        if c.category not in categories:
            catstring = categories[0]
            for i in categories[1:]:
                catstring = catstring + " or " + categories[i]
            #print name + " is not a " + catstring + " card."
            return None
        if c.cost > upto:
            #print name + " costs " + str(c.cost)
            return None
        return c
    
    def choose_discard(self,prompt):
        index = 0        
        while True:
            dis_card = self.discardtable1[index]
            c = self.getcard(dis_card,[dis_card],self.hand)
            if c:
                return c.name
            else:
                index+=1
            
    def yesnoinput(self,prompt,yesstring='',nostring=''):
        return True

    def show(self):
        pass

class TablePlayer(ComputerPlayer):
    def __init__(self,name):
        ComputerPlayer.__init__(self,name) 
        self.index=0
        self.buygaintable=[]
        q=re.match(r'([a-zA-Z]+)(\d+)',name)
        if q:
            self.number = q.group(2)
        else:
            print(name)
        self.playtable1 = ["Village","Festival","Market","Laboratory","Witch",
        "Council Room","Militia","Adventurer","Smithy","Bureaucrat","Moat",""]
        self.discardtable1 = ["Garden","Duchy","Province","Estate","Curse","Copper",
        "Village","Bureaucrat","Silver","Militia","Smithy","Council Room","Witch",
        "Festival","Market","Adventurer","Laboratory","Gold","Moat"]
    
    def turn(self,players,supply,trash):
        self.show()
        self.actions = 1
        self.buys = 1
        self.purse = 0
        #action phase
        self.index = 0
        while self.actions>0 and 'action' in catinlist(self.hand):
            playthis = self.playtable1[self.index]
            if playthis:
                c = self.getcard(playthis,supply,self.hand,"your hand",['action'])
                if c:
                    #print (self.name + " plays " + c.name)
                    self.actions = self.actions - 1
                    c.use(self,trash)
                    self.index=0                    
                    c.augment(self)
                    c.play(self,players,supply,trash)
                    self.show()
                else:
                    self.index += 1
            else:
                self.actions=0
        #buy phase
        v= self.number
        csvstring = r"Dominionbuy" + str(v) + ".csv"
        buydf=pandas.read_csv(csvstring,na_filter=False)
        sortedbuydf=buydf.sort_values("Buyvalues",ascending=False)
        ranktable = sortedbuydf.Cardname
        self.index = 0
        for c in self.hand:
            self.purse += c.buypower
        while self.buys>0:
            purchase = ranktable.iloc[self.index]
            if not purchase:
                break
            else:
                c = self.getcard(purchase,supply,upto=self.purse)
                if c:
                    self.discard.append(supply[purchase].pop())
                    self.index = 0
                    self.buys = self.buys -1
                    self.purse = self.purse - c.cost
                else:
                    self.index += 1
                    
        #cleanup phase
        self.discard = self.discard + self.played + self.hand + self.aside
        self.played = []
        self.hand = []
        self.aside = []
        for i in range(5):
            self.draw()
    
        
def gameover(supply):
    if len(supply["Province"])==0:
        return True
    out = 0
    for stack in supply:
        if len(supply[stack])==0:
            out+=1
    if out>=3:
        return True
    return False

def namesinlist(cardlist):
    namelist = []    
    for c in cardlist:
        namelist.append(c.name)
    return namelist

def catinlist(cardlist):
    catlist = []
    for c in cardlist:
        catlist.append(c.category)
    return catlist

def getcard(name,supply,target_list=None,target_name= "the supply anymore",categories=['action','coin','curse','victory'],upto=100):
    if not name in supply:
        print( name + " is not in this game.")
        return None
    if not target_list:
        target_list = supply[name]
    nameslist = namesinlist(target_list)
    if not name in nameslist:
        print ("There is no " + name + " in " + target_name)
        return None
    i = nameslist.index(name)
    c = target_list[i]
    if c.category not in categories:
        catstring = categories[0]
        for i in categories[1:]:
            catstring = catstring + " or " + categories[i]
        print (name + " is not a " + catstring + " card.")
        return None
    if c.cost > upto:
        print (name + " costs " + str(c.cost))
        return None
    return c

def totalbuypower(cardlist):
    TBP = 0
    for c in cardlist:
        TBP += c.buypower
        if c.category == "action":
            TBP += c.coins
    return TBP

def countsupply(supply,form):
    return [len(supply[a]) for a in form]

def countcards(cards,form):
    dcount = Counter(namesinlist(cards))
    return [dcount[a] for a in form]

def rankcards(form,vector):
    od = OrderedDict(zip(form,vector))
    sd = OrderedDict(sorted(od.items(),key = itemgetter(1),reverse=True))
    return list(sd.keys())
    
#import Dominion
#import random
from collections import defaultdict

#Get player names
player_names = ["Timothy","*Grover","*Elmo"]

#number of curses and victory cards
if len(player_names)>2:
    nV=12
else:
    nV=8
nC = -10 + 10 * len(player_names)

#Define box
box = {}
box["Woodcutter"]=[Woodcutter()]*10
box["Smithy"]=[Smithy()]*10
box["Laboratory"]=[Laboratory()]*10
box["Village"]=[Village()]*10
box["Festival"]=[Festival()]*10
box["Market"]=[Market()]*10
box["Chancellor"]=[Chancellor()]*10
box["Workshop"]=[Workshop()]*10
box["Moneylender"]=[Moneylender()]*10
box["Chapel"]=[Chapel()]*10
box["Cellar"]=[Cellar()]*10
box["Remodel"]=[Remodel()]*10
box["Adventurer"]=[Adventurer()]*10
box["Feast"]=[Feast()]*10
box["Mine"]=[Mine()]*10
box["Library"]=[Library()]*10
box["Garden"]=[Garden()]*nV
box["Moat"]=[Moat()]*10
box["Council Room"]=[Council_Room()]*10
box["Witch"]=[Witch()]*10
box["Bureaucrat"]=[Bureaucrat()]*10
box["Militia"]=[Militia()]*10
box["Spy"]=[Spy()]*10
box["Thief"]=[Thief()]*10
box["Throne Room"]=[Throne_Room()]*10

supply_order = {0:['Curse','Copper'],2:['Estate','Cellar','Chapel','Moat'],
                3:['Silver','Chancellor','Village','Woodcutter','Workshop'],
                4:['Garden','Bureaucrat','Feast','Militia','Moneylender','Remodel','Smithy','Spy','Thief','Throne Room'],
                5:['Duchy','Market','Council Room','Festival','Laboratory','Library','Mine','Witch'],
                6:['Gold','Adventurer'],8:['Province']}

#Pick 10 cards from box to be in the supply.
boxlist = [k for k in box]
random.shuffle(boxlist)
random10 = boxlist[:10]
supply = defaultdict(list,[(k,box[k]) for k in random10])


#The supply always has these cards
supply["Copper"]=[Copper()]*(60-len(player_names)*7)
supply["Silver"]=[Silver()]*40
supply["Gold"]=[Gold()]*30
supply["Estate"]=[Estate()]*nV
supply["Duchy"]=[Duchy()]*nV
supply["Province"]=[Province()]*nV
supply["Curse"]=[Curse()]*nC

#initialize the trash
trash = []

#Costruct the Player objects
players = []
for name in player_names:
    if name[0]=="*":
        players.append(ComputerPlayer(name[1:]))
    elif name[0]=="^":
        players.append(TablePlayer(name[1:]))
    else:
        players.append(Player(name))

#Play the game
turn  = 0
while not gameover(supply):
    turn += 1    
    print("\r")    
    for value in supply_order:
        print (value)
        for stack in supply_order[value]:
            if stack in supply:
                print (stack, len(supply[stack]))
    print("\r")
    for player in players:
        print (player.name,player.calcpoints())
    print ("\rStart of turn " + str(turn))    
    for player in players:
        if not gameover(supply):
            print("\r")
            player.turn(players,supply,trash)
            

#Final score
print ("\r")
for player in players:
    print (player.name,player.calcpoints())

print ("\n")
for player in players:
    print (player.name,player.cardsummary())