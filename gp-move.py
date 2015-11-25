from collections import defaultdict
import heapq
import sys

RECIPE_FILE = "outfile_4_1.txt"

USE_0HD = False

recipes = defaultdict(list)
recipe_strings = {}

def dijkstra(elbow0, dist0, elbow1, dist1):

    routes = {}
    q = [(0, elbow0, dist0, None, None)]

    while q:

        c1, e1, d1, e0, d0 = heapq.heappop(q)
        
        if (e1, d1) not in routes:
            routes[(e1, d1)] = c1, e0, d0
            
            if (e1, d1) == (elbow1, dist1):
                return routes, e1, d1

            for e2, d2, l1, c2 in recipes[e1]:

                if l1 is not None:
                    continue

                if (e2, d1+d2) not in routes:
                    heapq.heappush(q, (c1 + c2, e2, d1+d2, e1, d1))

def print_route(elbow0, dist0, elbow1, dist1):
    
    plain = ""
    ops = ""

    routes, e0, d0 = dijkstra(elbow0, dist0, elbow1, dist1)

    while (e0, d0) != (elbow0, dist0):

        e1, d1 = e0, d0
        cost, e0, d0 = routes[(e0, d0)]

        recipe = recipe_strings[(e0, e1, d1-d0, None)]
                            
        plain = recipe + plain

        ops = "%d %d %s %s %d: %s\n" % (cost,
                                           d1-d0,
                                           e0,
                                           e1,
                                           d1,
                                           recipe) + ops                

    print ops,
    print "\nm%d%s%s: %s\n" % (dist1-dist0, elbow0, elbow1, plain)    

# split s into runs of alpha characters followed by non-alpha characters
def to_tokens(s):

    if not s:
        return []

    tokens = []
    token = ""
    alpha = s[0].isalpha()

    for c in s:                
        if c == ":":
            break
        
        if c.isalpha() == alpha:
            token += c
        else:
            tokens.append(token)
            token = c
            alpha = not alpha

    tokens.append(token)
    return tokens

def reflect(elbow):
    return elbow[0] if elbow[-1] == "r" else elbow + "r"

def reflect_recipe(s):

    if USE_0HD:
        return s

    res = ""
    tokens = to_tokens(s)
    for i in range(len(tokens)):
        if tokens[i] in "oe":
            timing = int(tokens[i+1])
            if abs(timing) != 9999 and timing % 2:
                if tokens[i] == "o":
                    res += "e"
                elif tokens[i] == "e":
                    res += "o"
            else:
                res += tokens[i]
        elif tokens[i].strip():
            res += "%d " % -int(tokens[i])

    return res

def switch_phase(recipe):
    out_recipe = ""

    for c in recipe:
        if c == "o":
            out_recipe += "e"
        elif c == "e":
            out_recipe += "o"
        else:
            out_recipe += c

    return out_recipe

def read_recipes(filename):

    with open(filename) as f:
        for s in f:
            
            tokens = to_tokens(s)

            if tokens[0] == "Rev":
                continue

            i = 0
            side = lane = None
            if tokens[0][0] in "LR":
                side = tokens[0][0]
                lane = int(tokens[1])
                i += 2

            assert(tokens[i] == "m")

            move = int(tokens[i+1])

            elbow_in = tokens[i+2][0]
            elbow_out = tokens[i+2][1:]

            recipe_string = s[s.find(":")+2:].rstrip("\r\n")

#            Uncommment to use only central blocks as elbow
#            if tokens[i+2].count("A") != 2:
#                continue

            cost = s.count("e") + s.count("o")
                
            for c in "RL":
                if side is None or side == c:
                    recipes[elbow_in].append((elbow_out, move, lane, cost))
                    recipe_strings[(elbow_in, elbow_out, move, lane)] = recipe_string
                elbow_in = reflect(elbow_in)
                elbow_out = reflect(elbow_out)
                recipe_string = reflect_recipe(recipe_string)


read_recipes(RECIPE_FILE)

for arg in sys.argv[1:]:
    tokens = to_tokens(arg)
    assert(tokens[0] == "m")

    dist = int(tokens[1])

    idx = 2 if tokens[2][1] == "r" else 1

    elbow0 = tokens[2][:idx]
    elbow1 = tokens[2][idx:]

    print_route(elbow0, 0, elbow1, dist)
