from __future__ import print_function
import copy
import math
try:
    import Queue as Q  # ver. < 3.0
except ImportError:
    import queue as Q

class Problem(object):
    def __init__(self, h, r, c, p, g, sstate, gstates):
        self.heur = h
        self.row = r
        self.col = c
        self.piece = p
        self.goalcount = g
        self.start = sstate
        self.goals = gstates

    def __str__(self):
        result = "***Problem class***\nHeuristic Code: " + str(self.heur) + "\nRow:" + str(
            self.row) + "\nColumn:" + str(self.col) + "\nPieces:" + str(self.piece) + "\nGoal Count:" + str(
            self.goalcount)
        return result

def manh(state,other,r,c,p):
        distance=0
        for i in xrange(1,p+1):
            first=state.index(i)
            second=other.index(i)
            fx=first%c
            fy=first/c
            sx=second%c
            sy=second/c
            distance+=abs(fx-sx)+abs(fy-sy)
        return distance

def misplacedBlocks(state,other,r,c,p):
    score=0
    for i in xrange(1,p+1):
        first=state.index(i)
        second=other.index(i)
        if first!=second:
            score+=1
    
    return score

class Node(object):
    def __init__(self, state, par,r,c,p,h,g):
        self.state = state
        self.row = r
        self.col = c
        self.parent = par
        self.H = h
        self.G = g
        self.pieces=p

    def __eq__(self, other):
        return self.state == other.state

    def __str__(self):
        res = ''
        for i in xrange(self.row):
            for j in xrange(self.col):
                res += str(self.state[i * self.col + j]) + ' '
            res += '\n'
        #res+="H "+str(self.H)
        return res

    def __hash__(self):
        return hash(self.state)
    def __cmp__(self, other):
        return cmp(self.H+self.G,other.H+other.G)

    def legalmoves(self,pieces):
        legals=[]
        for piece in xrange(1,pieces+1):
            idx=self.state.index(piece)
            r=idx/self.col
            c=idx%self.col
            #for move up
            if(r!=0 and self.state[idx-self.col]==0):
                up=copy.deepcopy(self.state)
                up[idx-self.col]=piece
                up[idx]=0
                legals.append(up)
            #for move down
            if(r<self.row-1 and self.state[idx+self.col]==0):
                down=copy.deepcopy(self.state)
                down[idx+self.col]=piece
                down[idx]=0
                legals.append(down)
            #for move left
            if(c!=0 and self.state[idx-1]==0):
                left=copy.deepcopy(self.state)
                left[idx-1]=piece
                left[idx]=0
                legals.append(left)
            #for move right
            if(c!=self.col-1 and self.state[idx+1]==0):
                right=copy.deepcopy(self.state)
                right[idx+1]=piece
                right[idx]=0
                legals.append(right)
        return legals
    def checkRight(self,piece):
        flag=False
        for i in xrange(self.row):
            for j in xrange(self.col):
                if self.state[i*self.col+j]==piece:
                    if j+1<self.col:
                        if self.state[i*self.col+j+1]==piece:
                            continue
                        elif self.state[i*self.col+j+1]==0:
                            flag=True
                        else:
                            return False
                    else:
                        return False
        if flag==True:
            return True
        return False

    def checkUp(self,piece):
        flag=False
        for i in xrange(self.row):
            for j in xrange(self.col):
                if self.state[i*self.col+j]==piece:
                    if i>0:
                        if self.state[(i-1)*self.col+j]==piece:
                            continue
                        elif self.state[(i-1)*self.col+j]==0:
                            flag=True
                        else:
                            return False
                    else:
                        return False
        if flag==True:
            return True
        return False

    def checkLeft(self,piece):
        flag=False
        for i in xrange(self.row):
            for j in xrange(self.col):
                if self.state[i*self.col + j]==piece:
                    if j>0:
                        if self.state[i*self.col+j-1]==piece:
                            continue
                        elif self.state[i*self.col+j-1]==0:
                            flag=True
                        else:
                            return False
                    else:
                        return False
        if flag==True:
            return True
        return False
    def checkDown(self,piece):
        flag=False
        for i in xrange(self.row):
            for j in xrange(self.col):
                if self.state[i*self.col+j]==piece:
                    if i+1<self.row:
                        if self.state[(i+1)*self.col+j]==piece:
                            continue
                        elif self.state[(i+1)*self.col+j]==0:
                            flag=True
                        else:
                            return False
                    else:
                        return False
        if flag==True:
            return True
        return False
    def moveRight(self,piece):
        rght=copy.deepcopy(self.state)
        for i in xrange(self.row):
            for j in xrange(self.col-1,0,-1):
                if rght[i*self.col+j-1]==piece:
                    rght[i*self.col+j]=piece
                    rght[i * self.col + j - 1]=0
        return rght

    def moveLeft(self,piece):
        lft=copy.deepcopy(self.state)
        for i in xrange(self.row):
            for j in xrange(self.col-1):
                if lft[i*self.col+j+1]==piece:
                    lft[i * self.col + j] = piece
                    lft[i * self.col + j + 1] = 0
        return lft
    def moveUp(self,piece):
        up=copy.deepcopy(self.state)
        for i in xrange(self.row-1):
            for j in xrange(self.col):
                if up[(i+1)*self.col+j]==piece:
                    up[i*self.col+j]=piece
                    up[(i + 1) * self.col + j] =0
        return up
    def moveDown(self,piece):
        dwn= copy.deepcopy(self.state)
        for i in xrange(self.row-1,0,-1):
            for j in xrange(self.col):
                if dwn[(i - 1) * self.col + j] == piece:
                    dwn[i * self.col + j] = piece
                    dwn[(i - 1) * self.col + j] = 0
        return dwn
    def movesLikeJagger(self):
        legals=[]
        for i in xrange(1,self.pieces+1):
            if self.checkRight(i):
                legals.append(self.moveRight(i))
            if self.checkLeft(i):
                legals.append(self.moveLeft(i))
            if self.checkUp(i):
                legals.append(self.moveUp(i))
            if self.checkDown(i):
                legals.append(self.moveDown(i))
        return legals

def getMin(liste):
    min=float("inf")
    idx=-1
    for i in xrange(len(liste)):
        if liste[i].H + liste[i].G < min:
            min=liste[i].H + liste[i].G
            idx=i
    thing=liste[idx]
    del liste[idx]
    return thing

def inList(liste,state):
    idx = -1
    for i in xrange(len(liste)):
        if liste[i].state==state:
            idx=i
    return idx

def aStar(start,goal,heur):
        frontier=[]
        explored=[]
        current=start
        frontier.append(current)
        while len(frontier)!=0:
            current=getMin(frontier)
            if current.state==goal.state:
                path=[]
                while current.parent:
                    path.append(current)
                    current = current.parent
                path.append(current)
                return path[::-1]
            explored.append(current)
            neighbors=[]
            neighbors=current.movesLikeJagger()
         
            for n in neighbors:
                if n==[]:
                    continue
                gScore = current.G + 1

                if heur==0:
                    hScore = manh(n, goal.state, goal.row, goal.col, goal.pieces)
                else:
                    hScore=misplacedBlocks(n,goal.state,goal.row,goal.col,goal.pieces)

                if inList(frontier,n)==-1 and inList(explored,n)==-1:
                    newNode=Node(n,current,current.row,current.col,current.pieces,hScore,gScore)
                    frontier.append(newNode)
                else:
                    if inList(frontier,n)!=-1 and gScore<frontier[inList(frontier,n)].G:
                        frontier[inList(frontier,n)].parent=current
                        frontier[inList(frontier, n)].G=gScore
                    elif inList(explored,n)!=-1 and gScore<explored[inList(explored,n)].G:
                        del explored[inList(explored,n)]
                        newNode = Node(n, current, current.row, current.col, current.pieces, hScore, gScore)
                        frontier.append(newNode)

        return []



#Gets input
f = open('die.inp', 'r')
# get question number
qcount = int(f.readline())

for pIndex in xrange(qcount):
    # get heuristic type
    ftype = int(f.readline())

    # get row,col,pieces,number of goal states
    s = f.readline().split()
    rows = int(s[0])
    cols = int(s[1])
    pieces = int(s[2])
    gcount = int(s[3])

    s = f.readline()  # should give S
    start = []
    for i in xrange(rows):
        s = f.readline().split()
        for j in xrange(cols):
            start.append(int(s[j]))

    goals = [[0 for x in range(rows * cols)] for y in range(gcount)]
    for i in xrange(gcount):
        z = f.readline()  # should give F
        for j in xrange(rows):
            s = f.readline().split()
            for k in xrange(cols):
                goals[i][j * cols + k] = (int(s[k]))
    #print("this is " + str(pIndex)+". problem")
    mels = Problem(ftype, rows, cols, pieces, gcount, start, goals)
    noo = Node(start, None, rows, cols, pieces,0,0)
    #to find the goal with smallest path
    enter = raw_input()
    while(enter != ''):
        enter = raw_input()
    reses=[]
    tmin=float("inf")
    idx=-1
    for t in xrange(len(goals)):
        endd = Node(goals[t], None, rows, cols,pieces,0,0)
        localres=aStar(noo,endd,ftype)
        reses.append(localres)
        if(len(localres)<tmin and len(localres)!=0):
            tmin=len(localres)
            idx=t
    for nod in reses[idx]:
        print(nod)

f.close()



