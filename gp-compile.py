from collections import defaultdict
import heapq
import sys

RECIPE_FILE = "outfile_4_1.txt"

USE_0HD = False

recipes = defaultdict(list)
recipe_strings = {}

def dijkstra(elbow, dist, lanes):

    routes = {}
    q = [(0, len(lanes), elbow, dist, None, None, None)]

    while q:

        c1, remaining, e1, d1, e0, d0, l0 = heapq.heappop(q)
        
        if (remaining, e1, d1) not in routes:
            routes[(remaining, e1, d1)] = c1, e0, d0, l0
            
            if remaining == 0:
                return routes, e1, d1

            for e2, d2, l1, c2 in recipes[e1]:

                if l1 is not None:
                    if l1 + d1 != lanes[-remaining]:
                        continue
                    else:
                        hit = 1
                else:
                    hit = 0

                if (remaining-hit, e2, d1+d2) not in routes:
                    heapq.heappush(q, (c1 + c2, remaining-hit, e2, d1+d2, e1, d1, l1))

def lookahead(elbow, dist, lanes, parities, lookahead):
    
    plain = ""
    allcost = 0

    for i in range(len(lanes)):

        lookahead_lanes = lanes[i:i+lookahead]
        lookahead_gliders = len(lookahead_lanes)

        routes, e0, d0 = dijkstra(elbow, dist, lookahead_lanes)

        remaining = 0
        found_first_glider = False
        subplain = ""
        ops = ""
#        print "Begin backtrace"

        while (remaining, e0, d0) != (lookahead_gliders, elbow, dist):

            e1, d1 = e0, d0
            cost, e0, d0, lane = routes[(remaining, e0, d0)]
#            print "\t\t", cost, e0, d0, lane

            if lane is not None:
                remaining += 1

            if remaining == lookahead_gliders and not found_first_glider:
                found_first_glider = True
                next_cost, next_elbow, next_dist = cost, e1, d1

            if found_first_glider:
                
                recipe = recipe_strings[(e0, e1, d1-d0, lane)]

                if parities[i]:
                    recipe = switch_phase(recipe)

                subplain = recipe + subplain

                ops = "%d %s %d %s %s %d: %s\n" % (allcost+cost,
                                                   str(lane),
                                                   d1-d0,
                                                   e0,
                                                   e1,
                                                   d1,
                                                   recipe) + ops                
        elbow, dist = next_elbow, next_dist
        allcost += next_cost

        plain += subplain
        print ops,

    print "\nfull_recipe: " + plain
    print "\n%d / %d = %f" % (allcost, len(lanes), float(allcost) / len(lanes))
    

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

input_string = ""

for s in sys.stdin:
    input_string += s

idx = input_string.find(":")
if idx >= 0:
    input_string = input_string[idx+1:]

lanes = []
parities = []

tokens = to_tokens(input_string)

for i in range(0, len(tokens), 2):
    if "E" in tokens[i]:
        parities.append(0)
    elif "O" in tokens[i]:
        parities.append(1)
    else:
        assert(False)

    # convert from quarter diagonals to half diagonals
    lanes.append(int(tokens[i+1]) // 2 + 1)

lookahead("A", 0, lanes, parities, 6)
