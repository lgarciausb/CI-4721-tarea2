import json
import rustworkx as rx

class Parser(object):
    def __init__(self):
        self.T = ["$"]
        self.NT = set()
        self.R = []
        self.I = None
        self.P = [[" "]]
        self.f = self.g = {}

    def addRule(self, cs):
        R = [cs[0], cs[1:]]
        if R in self.R: return 0

        self.NT.add(R[0])
        i = isNT(R[1][0])

        for e in range(i,len(R[1]),2):
            if R[1][e] not in self.T and R[1][e] != "":
                self.T.append(R[1][e])
                for row in self.P: row.append(" ")
                self.P.append([" " for _ in range(len(self.P)+1)])
                self.P[0][-1] = "<"
                self.P[-1][0] = ">"
        for e in range(i^1,len(R[1]),2):
            self.NT.add(R[1][e])

        self.R.append(R)
        return 1
    
    def addPrec(self, cs):
        a, op, b = cs
        if a not in self.T: return a
        if b not in self.T: return b
        self.P[self.T.index(a)][self.T.index(b)] = op
        return 1
    
    def build(self):
        if self.I == None: return -1
        G = rx.PyDiGraph()
        node_groups = {}
        # node order is f_i, g_i per terminal symbol
        # so for symbols [a,b] we have [f_a, g_a, f_b, g_b] 
        # f_is have indexes 2n and g_i indexes 2n+1
        for i in range(len(self.T)):
            G.add_node(0)
            G.add_node(0)
            node_groups["f"+self.T[i]] = 2*i
            node_groups["g"+self.T[i]] = 2*i+1
        for row in range(len(self.P)):
            for col in range(len(self.P)):
                if self.P[row][col] == ">":
                    G.add_edge(2*row, 2*col+1, -1)
                elif self.P[row][col] == "<":
                    G.add_edge(2*col+1, 2*row, -1)
        for row in range(len(self.P)):
            for col in range(len(self.P)):
                if self.P[row][col] == "=":
                    G.merge_nodes(row*2, col*2+1)
                    node_groups["f"+self.T[row]] = node_groups["g"+self.T[col]]
        if rx.digraph_find_cycle(G) != []:
            return 0
        self.f = {}
        self.g = {}
        for i in range(len(self.T)):
            paths = rx.bellman_ford_shortest_paths(G, node_groups["f"+self.T[i]], weight_fn = lambda x: -1)
            if len(paths) == 0:  
                self.f[self.T[i]] = 0
            else:
                self.f[self.T[i]] = len(max(paths.values(), key=lambda x: len(x)))-1
            paths = rx.bellman_ford_shortest_paths(G, node_groups["g"+self.T[i]], weight_fn = lambda x: -1)  
            if len(paths) == 0: 
                self.g[self.T[i]] = 0
            else:
                self.g[self.T[i]] = len(max(paths.values(), key=lambda x: len(x)))-1

        return 1
    
    def parse(self, string):
        if len(self.f) == 0 and len(self.g) == 0: return -1
        if not all(c in self.T for c in string): return -2
        string = list(string + "$")
        stack = ["$"]
        res = []
        e = string[0]
        print("\t" + "stack" +"\t\t"+ "input" +"\t"+ "action")
        while 1:
            p = stack[-1]
            row = self.T.index(p)
            col = self.T.index(e)
            print("".join(res) +"\t"+ "".join(stack) +"\t"+ self.P[row][col] +"\t"+ "".join(string) + "\t", end='')
            if p == "$" and e == "$": 
                if res != [self.I]:
                    print("reject, cannot find rule to reduce with")
                    return 0
                print("accept")
                return 1
            if self.f[p] <= self.g[e]:
                res.append(e)
                stack.append(string.pop(0))
                e = string[0]
                print("read")
            elif self.f[p] > self.g[e]:
                x = stack.pop()
                while not self.f[stack[-1]] < self.g[x[-1]]:
                    x = stack.pop()
                reduced = False
                for R in self.R:
                    if x in R[1] and res[-len(R[1]):] == R[1]:
                        res = res[:-len(R[1])] + [R[0]]
                        x = R[0]
                        reduced = True
                        print(f"reduce with {R[0]} → {''.join(R[1])}")
                        break
                if reduced == False: 
                    print("reject, cannot find rule to reduce with")
                    return 0

           



def isNT(c):
    return c.isupper() and c.isalpha()

def isT(c):
    return (c.islower() and c.isalpha()) or (c.isascii() and not c.isalpha() and not c.isnumeric() and c != "$")

def isSymbol(c):
    return isT(c) or isNT(c)

def checklens(cs):
    for i in range(1,len(cs)):
        if len(cs[i]) > 1: return i
    return -1

def isValidRule(cs):
    e = isT(cs[2])
    return all(e == isT(cs[i]) for i in range(2,len(cs),2)) and all(e != isT(cs[i]) for i in range(3,len(cs),2))


P = Parser()

while True:

    command = input(">").strip().split(" ")
    l = len(command)

    if command[0] == "": continue

    if command[0] == "RULE":
        if l < 2:
            print("use: RULE <non-terminal> [<symbol>]")
            continue
        i = checklens(command)
        if i != -1:
            print("invalid symbol: " + command[i])
            continue
        if not isNT(command[1]):
            print("first argument must be non-terminal symbol")
            continue
        if l == 2: command.append("")
        if not isValidRule(command):
            print("invalid rule: " + " ".join(command[2:]))
            continue

        if P.addRule(command[1:]):
            print(f"added rule: {P.R[-1][0]} → {''.join(P.R[-1][1])}")
        else: 
            print(f"rule already exists: {P.R[-1][0]} → {''.join(P.R[-1][1])}")

    elif command[0] == "INIT":
        if l < 2:
            print("use: INIT <non-terminal>")
            continue
        if l > 2:
            print("Unknown argument: " + command[2])
            print("use: INIT <non-terminal>")
            continue
        i = checklens(command)
        if i != -1:
            print("invalid symbol: " + command[i])
            continue
        if not isNT(command[1]):
            print("first argument must be non-terminal symbol")
            continue
        if command[1] not in P.NT:
            print(f"non-terminal symbol {command[1]} not found")
            continue
        P.I = command[1]
        print(f"set {P.I} as initial symbol")

    elif command[0] == "PREC":
        if l < 4:
            print("use: PREC <terminal> <op> <terminal>")
            continue
        if l > 4:
            print("Unknown argument: " + command[4])
            print("use: PREC <terminal> <op> <terminal>")
            continue
        for i in [1,3]:
            if not isT(command[i]): 
                print(["first", "third"][i] + " argument must be non-terminal symbol")
                continue 
        if command[2] not in ("<", ">", "="):
            print("second argument must be precedence operator (<, >, =)")
            continue 
        
        res = P.addPrec(command[1:])
        if  res != 1:
            print(f"symbol {res} not found")
            continue

        print("set precedence " + " ".join(command[1:]))

    elif command[0] == "BUILD":
        if l > 1:
            print("Unknown argument: " + command[1])
            print("use: BUILD")
            continue
        res = P.build()
        if res == 0:
            print("cannot build f and g tables")
            continue
        if res == -1:
            print("initial symbol has not been provided")
            continue
        print("values for f")
        for symbol in P.f:
            print(f"{symbol}: {P.f[symbol]}")
        print("values for g")
        for symbol in P.g:
            print(f"{symbol}: {P.g[symbol]}")

    elif command[0] == "PARSE":
        if l < 2:
            print("use: PARSE <string>")
            continue
        string = "".join(command[1:])
        if not all (isT(c) for c in string):
            print("all string characters must be valid terminal symbols")
            continue

        res = P.parse(string)
        if res == -1:
            print("grammar has not been built")
            continue
        if res == -2:
            print("string has unrecognized terminal symbols")
            continue

    elif command[0] == "SAVE":
        if l > 2:
            print("Unknown argument: " + command[1])
            print("use: SAVE [<filename>]")
            continue
        
        if l == 1:
            command.append("parser")
        f = open(command[1] + ".json", "w")
        f.write(json.dumps(
            {
                "T" : P.T,
                "NT" : list(P.NT),
                "R" : P.R,
                "I" : P.I,
                "P" : P.P
            }
        ))
        f.close()
        print("parser saved at " + command[1] + ".json")

    elif command[0] == "LOAD":
        if l > 2:
            print("Unknown argument: " + command[1])
            print("use: LOAD [<filename>]")
            continue
        
        if l == 1:
            command.append("parser")
        try:
            f = open(command[1] + ".json", "r")
            PJ = json.loads(f.read())
            P.T = PJ["T"]
            P.NT = set(PJ["NT"])
            P.R = PJ["R"]
            P.I = PJ["I"]
            P.P = PJ["P"]
            f.close()
            print("parser loaded from " + command[1] + ".json")
        except:
            print(f"file {command[1] + '.json'} not found or invalid")

    elif command[0] == "SHOW":
        if l > 1:
            print("Unknown argument: " + command[1])
            print("use: SHOW")
            continue

        print("Terminals: " + " ".join(P.T))
        print("Non-Terminals: " + ", ".join(P.NT))
        print("Rules:\n\t" + "\n\t".join([f"{R[0]} → {''.join(R[1])}" for R in P.R]))
        print("Initial symbol: " + (P.I if P.I != None else ""))
        print("Precedence table:")
        print("  " + " ".join(P.T))
        for i in range(len(P.P)):
            print(f"{P.T[i]} " + " ".join(P.P[i]))

    elif command[0] == "RESET":
        if l > 1:
            print("Unknown argument: " + command[1])
            print("use: RESET")
            continue

        P = Parser()
        print("parser reset")

    elif command[0] == "EXIT": exit()
    else: print("invalid command")