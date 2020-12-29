# -*- coding: utf-8 -*-
"""
Created on Tue Oct 13 15:26:55 2015

@author: tfleck
"""
#0. Import modules
import random
import re
import pandas

#1. Define Supply methods
class Supply(pandas.DataFrame):
    def lsi(self):
        return list(self.index)
    def gameover(self):
        if self.loc['Province','quantity']==0:
            return True
        else:
            return len(self[self['quantity']==0])>2
    def remove(self,cname):
        self.loc[cname,'quantity']-=1
    def has(self,cname):
        if self.quantity[cname]>0:
            return True
        else:
            return False

#2. Define card classes
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

class Gardens(Victory_card):
    def __init__(self):
        Victory_card.__init__(self,"Gardens",4,0)

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
                while True:
                    pick = input("Choose a coin to gain.  Any coin up to " + str(c.cost+3)+": ")
                    if pick:
                        g = getcard(pick,supply,categories=["coin"],upto=c.cost+3)
                        if g:
                            player.hand.append(g)
                            supply.remove(pick)
                            break
                        else:
                            continue
                    else:
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
        player.show(lead="\n")        
        return player.yesnoinput(player.name + ", you have a " + self.name +
                        " in your hand.  Do you want to block the attack?")

class Council_Room(Action_card):
    def __init__(self):
        Action_card.__init__(self,"Council Room",5,0,3,1,0)
    def play(self,this_player,players,supply,trash):
        for player in players_around(players,this_player,inclusive=True):
            player.draw()

class Witch(Action_card):
    def __init__(self):
        Action_card.__init__(self,"Witch",5,0,2,0,0)
    def play(self,this_player,players,supply,trash):
        for player in players_around(players,this_player,inclusive=False):
            if supply.has("Curse"):
                for c in player.hand:
                    if c.react(player):
                        break
                else:
                    player.discard.append(Curse())
                    supply.remove("Curse")

class Bureaucrat(Action_card):
    def __init__(self):
        Action_card.__init__(self,"Bureaucrat",4,0,0,0,0)
    def play(self,this_player,players,supply,trash):
        if supply.has("Silver"):
            this_player.deck.insert(0,Silver())
            supply.remove("Silver")
        for player in players_around(players,this_player,inclusive=False):
            for c in player.hand:
                if c.react(player):
                    break
            else:
                if "victory" in catinlist(player.hand):
                    while True:                        
                        player.show(lead="\n\n")
                        putback = player.choose_discard(player.name + ", which victory card" +
                        " do you want to put on top of your deck?\n--> ")
                        c = getcard(putback,supply,player.hand,"your hand",["victory"])
                        if c:
                            player.hand.remove(c)
                            player.deck.insert(0,c)
                            break
                else:
                    player.show(lead="\n\n")
                        
class Militia(Action_card):
    def __init__(self):
        Action_card.__init__(self,"Militia",4,0,0,0,2)
    def play(self,this_player,players,supply,trash):
        for player in players_around(players,this_player,inclusive=False):
            if len(player.hand)>3:
                for c in player.hand:
                    if c.react(player):
                        break
                else:
                    player.show(lead="\n\n")
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
        for player in players_around(players,this_player,inclusive=True):
            for c in player.hand:
                if c.react(player):
                    break
            else:
                b = player.draw([])
                if not b:
                    continue
                else:
                    this_player.hprint("The first card in the deck of " + player.name + " is " + b.name)
                    if this_player.yesnoinput(this_player.name + ", do you want " + player.name + " to discard this?",
                    ", discard",", keep"):
                        player.discard.append(b)
                    else:
                        player.deck.insert(0,b)

class Thief(Action_card):
    def __init__(self):
        Action_card.__init__(self,"Thief",4,0,0,0,0)
    def play(self,this_player,players,supply,trash):
        for player in players_around(players,this_player,inclusive=False):
            for c in player.hand:
                if c.react(player):
                    break
            else:
                for i in range(2):
                    player.draw(player.hold)
                this_player.hprint(( player.name, namesinlist(player.hold)))
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

#3. Define player classes
class Player():

    def __init__(self,name,order):
        self.name = name
        self.order = order
        self.cycles = 0
        self.hand = []
        self.deck = [Copper()]*7 + [Estate()]*3
        random.shuffle(self.deck)
        self.played = []
        self.discard = []
        self.aside = []
        self.hold = []
        for i in range(5):
            self.draw()

    def stack(self):
        return (self.deck + self.hand + self.played + self.discard + self.aside + self.hold)

    def draw(self,dest=None):
        #defualt destination is player's hand
        if dest==None:
            dest = self.hand
        #Replenish deck if necessary and possible.
        if len(self.deck)==0 and len(self.discard)>0:
            self.deck = self.discard
            self.discard = []
            random.shuffle(self.deck)
            self.cycles +=1
        #If deck has cards, add card to destination list
        if len(self.deck)>0:
            c = self.deck.pop(0)
            dest.append(c)
            return c

    def start_turn(self):
        self.actions=1
        self.buys=1
        self.purse=0
        
    def cleanup(self):
        self.discard = self.discard + self.played + self.hand + self.aside
        self.played = []
        self.hand = []
        self.aside = []
        for i in range(5):
            self.draw()

    def playcard(self,c,players,supply,trash):
        self.actions -= 1
        c.use(self,trash)
        c.augment(self)
        c.play(self,players,supply,trash)
        
    def choose_action(self):
        return str(input("Which card would you like to play?  You have "\
                             + str(self.actions) + " action(s).\
                             \n-Hit enter for no play. --> "))
        
    def choose_buy(self,supply,players):
        buy_string = "Buying power is " + str(self.purse) + ".  You have " + str(self.buys) + " buy"
        if self.buys>1:
            buy_string += "s"
        buy_string += ". "
        purchase = input(buy_string+"What would you like to purchase?  \n-Hit enter for no purchase.-   --> ")
        return purchase
    
    def turn(self,players,supply,trash):
        self.start_turn()
        #action phase
        while self.actions>0 and 'action' in catinlist(self.hand):
            self.show(lead="\n")
            playthis = self.choose_action()
            if playthis:
                c = getcard(playthis,supply,self.hand,"your hand",['action'])
                if c:
                    self.cprint(self.name + " plays " + c.name+ ". ")
                    self.playcard(c,players,supply,trash)
            else:
                break
        #buy phase
        for c in self.hand:
            self.purse += c.buypower
        self.show(lead="\n")
        while self.buys>0:
            purchase = self.choose_buy(supply,players)
            if not purchase:
                break
            else:
                c = getcard(purchase,supply,upto=self.purse)
                if c:
                    self.discard.append(c)
                    supply.remove(purchase)
                    self.buys = self.buys -1
                    self.purse = self.purse - c.cost
                    self.cprint(self.name + " bought " + c.name+". ")
        self.cleanup()

    def gaincard(self,supply,upto):
        while True:
            gain = input("What would you like to get?  Any card up to " + str(upto) + "\n--> ")
            c = getcard(gain,supply,upto=upto)
            if c:
                self.discard.append(c)
                supply.remove(gain)
                break
            
    def yesnoinput(self,prompt,yesstring='',nostring=''):
        self.hprint(prompt + "\n1 - Yes" + yesstring + "\n0 - No" + nostring)
        while True:
            r = input("--> ")        
            if r == "0":
                return False
            if r == "1":
                return True    
    
    def choose_discard(self,prompt):
        return str(input(prompt))

    def hprint(self,string):
        print(string)
    def cprint(self,string):
        pass
    
    def show(self,lead=""):
        print (lead+self.name)
        print ("hand:", ", ".join(namesinlist(self.hand)))
        if len(self.deck)>0:
            print ("deck (alphabetical order):", ", ".join(sorted(namesinlist(self.deck))))
        if len(self.discard)>0:
            print ("discard:", ", ".join(sorted(namesinlist(self.discard))))
        if len(self.played)>0:
            print ("played:", ", ".join(sorted(namesinlist(self.played))))
        if len(self.aside)>0:
            print ("aside:", ", ".join(sorted(namesinlist(self.aside))))
    
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
        summary['Total cards']=len(self.stack())
        summary['VICTORY POINTS']=self.calcpoints()
        return summary

    def calcpoints(self):
        tally = 0
        gardens = 0
        n = 0
        for c in self.stack():
            tally += c.vpoints
            n += 1
            if c.name == "Gardens":
                gardens+=1
        return tally + n//10 * gardens

class ComputerPlayer(Player):

    def __init__(self,name,order,supply,sp):
        Player.__init__(self,name,order)
        #beginning and middle of game
        bg1 = ["Province","Gold","Laboratory","Festival","Witch",
        "Council Room","Market","Militia","Adventurer","Smithy","Bureaucrat","Silver","Moat",""]
        self.buygaintable1 = [i for i in bg1 if i in supply.lsi()]
        #end of game        
        bg2 = ["Province","Gardens","Duchy","Estate","Gold","Silver",""]
        self.buygaintable2 = [i for i in bg2 if i in supply.lsi()]
        #beginning and middle of the game, too many action cards
        bg3 =  ["Province","Gold","Festival","Laboratory","Market","Village",
        "Silver",""]
        self.buygaintable3 = [i for i in bg3 if i in supply.lsi()]
        action_order = ["Village","Festival","Market","Laboratory","Witch",
        "Council Room","Militia","Adventurer","Smithy","Bureaucrat","Moat"][::-1]
        self.playtable1 = [i for i in action_order if i in supply.lsi()]
        discard_order = ["Gardens","Duchy","Province","Estate","Curse","Copper",
        "Village","Bureaucrat","Silver","Militia","Smithy","Council Room","Witch",
        "Festival","Market","Adventurer","Laboratory","Gold","Moat"]
        self.discardtable1 = [i for i in discard_order if i in supply.lsi()]
        self.sp=sp
        self.loglist=[]
        self.logdf=pandas.DataFrame()
    
    def choose_action(self):
        self.hand.sort(key = lambda x: Findex(x.name,self.playtable1))
        return self.hand[-1].name
    
    def choose_buy(self,supply,players):
        if supply.quantity["Province"]>len(players)+totalbuypower(self.deck)/8:
            if self.action_balance()<-10:
                bgt = self.buygaintable3
            else:
                bgt = self.buygaintable1
        else:
            bgt = self.buygaintable2
        for c in bgt:
            if supply.has(c) and supply.cost[c]<=self.purse:
                return c
        else:
            return ""

    def choose_discard(self,prompt):
        self.hand.sort(key = lambda x: Findex(x.name,self.discardtable1))        
        return self.hand[0].name

    def turn(self,players,supply,trash):
        self.start_turn()
        self.log(players,supply,trash)
        #action phase
        while self.actions>0 and 'action' in catinlist(self.hand):
            playthis = self.choose_action()
            if playthis:
                c = getcard(playthis,supply,self.hand,"your hand",['action'])
                if c:
                    self.cprint(self.name + " plays " + c.name+ ". ")
                    self.playcard(c,players,supply,trash)
            else:
                break
        
        #buy phase
        for c in self.hand:
            self.purse += c.buypower
        self.show(lead="\n")
        while self.buys>0:
            purchase = self.choose_buy(supply,players)
            if not purchase:
                break
            else:
                c = getcard(purchase,supply,upto=self.purse)
                if c:
                    self.discard.append(c)
                    supply.remove(purchase)
                    self.buys = self.buys -1
                    self.purse = self.purse - c.cost
                    self.cprint(self.name + " bought " + c.name+". ")
                else:
                    self.index += 1
                    
        self.cleanup()
    
    def yesnoinput(self,prompt,yesstring='',nostring=''):
        return True

    def hprint(self,string):
        pass
    
    def cprint(self,string):
        if not self.sp:
            print(string)
    
    def show(self,lead=""):
        pass
    
    def log(self,players,supply,trash):
        pass

class TablePlayer(ComputerPlayer):
    def __init__(self,name,adjust_df,order,supply,sp):
        ComputerPlayer.__init__(self,name,order,supply,sp) 
        self.index=0
        if adjust_df is None:
            adjust_df=pandas.read_csv('adjustment_matrix.csv',index_col=0)
        self.df=adjust_df.copy()
        self.local_adj=self.df.loc[supply.lsi(),supply.lsi()]
        sv=self.local_adj.sum().sort_values(ascending=False)
        sv=sv[sv>0]
        self.buygaintable1=list(sv.index)
    
    
#4. Define global functions        
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

def getcard(name,supply,target='supply',target_name= "the supply anymore",categories=['action','coin','curse','victory'],upto=100):
    if not name in supply.index:
        print( name + " is not in this game.")
        return None
    if supply.category[name] not in categories:
        print (name + " is not a(n) " + " or ".join(categories) + " card.")
        return None
    if supply.cost[name] > upto:
        print (name + " costs " + str(supply.cost[name]))
        return None
    
    if target=='supply':
        if supply.has(name):
            return supply.card[name]
        else:
            print ("There is no " + name + " in " + target_name)
            return None
    else:
        nameslist = namesinlist(target)
        if name in nameslist:
            i=nameslist.index(name)
            return target[i]
        else:
            print ("There is no " + name + " in " + target_name)
            return None

def totalbuypower(cardlist):
    TBP = 0
    for c in cardlist:
        TBP += c.buypower
        if c.category == "action":
            TBP += c.coins
    return TBP

def cardsummaries(players):
    cardsums={}
    for player in players:
        cardsums[player.name]=player.cardsummary()
    return pandas.DataFrame(cardsums).fillna(0).astype(int)

def players_around(players,this_player,inclusive=False):
    around=players[this_player.order:]+players[:this_player.order]
    if inclusive:
        return around[:]
    else:
        return around[1:]
    
def Findex(item,List):
    try:
        return List.index(item)
    except:
        return -1

def analyze_results(players,supply,trash,turn,winners):
    return supply.lsi()

#5. Define game execution        
def playgame(player_names,suppress_printing):
    sp = suppress_printing
    Nplay=len(player_names)
    #choose cards for initial supply
    startq={}
    startq['action']=10
    startq['curse']=10*(Nplay-1)
    startq['victory']=8+4*(Nplay>2)
    startq['Copper']=60-7*Nplay
    startq['Silver']=40
    startq['Gold']=30
    card_list = [Copper(),Silver(),Gold(),Curse(),Estate(),Duchy(),Province()]
    random10=[Adventurer(),Bureaucrat(),Cellar(),Chancellor(),Chapel(),Council_Room(),
            Feast(),Festival(),Laboratory(),Library(),Market(),Militia(),Mine(),
            Moat(),Moneylender(),Remodel(),Smithy(),Spy(),Thief(),Throne_Room(),
            Village(),Witch(),Woodcutter(),Workshop(),Gardens()]
    random.shuffle(random10)
    card_list = card_list + random10[:10]
    name_list = [c.name for c in card_list]
    cost_list = [c.cost for c in card_list]
    cat_list = [c.category for c in card_list]
    quantity_list = [0]*len(card_list)
    for i,v in enumerate(cat_list):
        try:
            quantity_list[i]=startq[v]
        except:
            quantity_list[i]=startq[name_list[i]]
    

    supply = Supply(data={"cost":cost_list,"category":cat_list,"quantity":quantity_list,
                          "card":card_list},index=name_list)
    supply.sort_values(by="cost",inplace=True)
    
    #initialize the trash
    trash = []
    
    #Costruct the Player objects
    players = []
    for play_order,name in enumerate(player_names):
        if type(name) is tuple:
           players.append(TablePlayer(name[0],name[1],play_order,supply,sp)) 
        elif name[0]=="*":
            players.append(ComputerPlayer(name[1:],play_order,supply,sp))
        else:
            players.append(Player(name,play_order))
    
    #Play the game
    turn  = 0
    while True:
        turn += 1
        if not sp:
            print('\n\nSUPPLY')
            print(supply[["cost","quantity"]])
            print('\r')
            print(cardsummaries(players).loc[['Total cards','VICTORY POINTS']])
            print("\nStart of turn " + str(turn))    
        for player in players:  
            player.turn(players,supply,trash)
            last_turn=player.order
            if supply.gameover():
                break
        else:
            continue
        break

    #Final scores and winners
    dcs=cardsummaries(players)
    vp=dcs.loc['VICTORY POINTS']
    vpmax=vp.max()
    high_scores2=[]
    high_scores1=[]
    for player in players:
        if vp.loc[player.name]==vpmax:
            if player.order>last_turn:
                high_scores2.append(player.name)
            else:
                high_scores1.append(player.name)
    if len(high_scores2)>0:
        winners=high_scores2
    else:
        winners=high_scores1
    
    if sp:
        return winners,analyze_results(players,supply,trash,turn,winners)
    else:
        if len(winners)>1:
            winstring= ' and '.join(winners) + ' win!'
        else:
            winstring = ' '.join([winners[0],'wins!'])
        if not sp:
            print("\n\nGAME OVER!!!   "+winstring+"\n")
        
        display_order='Adventurer,Bureaucrat,Cellar,Chancellor,Chapel,Council Room,\
        ,Feast,Festival,Laboratory,Library,Market,Militia,Mine,Moat,Moneylender,\
        ,Remodel,Smithy,Spy,Thief,Throne Room,Village,Witch,Woodcutter,Workshop,\
        ,Gold,Silver,Copper,Province,Duchy,Gardens,Estate,Curse,Total cards,\
        ,VICTORY POINTS'.split(',')
        newindex=[card for card in display_order if card in dcs.index]
        print(dcs.reindex(newindex))
        print("\n")       

#6. Play game when the file is called
if __name__ == "__main__":
    adf=pandas.read_csv('adjustment_matrix.csv',index_col=0)
    names1=["Alex","*Ben",("Cynthia",adf)]
    playgame(names1,suppress_printing=False)
