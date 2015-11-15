import golly as g
from time import time
from glife.text import make_text
#import cProfile, pstats

LANE1 = -5
LANE2 = 5
FULL_DEPTH = 4
CLEANUP_DEPTH = 1
MAX_POP = [40, 40, 40, 40, 30, 30, 30, 30]

GENS = 200
MAX_DIFF = 60

OUTFILE = '/home/user/life/outfile%d.txt' % time()

def to_pairs(cells):
    return zip(cells[::2], cells[1::2])

G_NE = g.parse('3o$2bo$bo!')
G_NW = g.parse('3o$o$bo!')
G_SW = g.transform(g.parse('bo$o$3o!'), 0, -2)
G_SE = g.transform(g.parse('bo$2bo$3o!'), -2, -2)

LWSS_W = g.transform(g.parse('bo2bo$o$o3bo$4o!'), 0, -1)
LWSS_S = g.transform(g.parse('bobo$o$o$o2bo$3o!'), -2, -4)

GLIDERS_SW = [to_pairs(g.evolve(G_SW, i)) for i in range(4)]
GLIDERS_SE = [to_pairs(g.evolve(G_SE, i)) for i in range(4)]
GLIDERS_NW = [to_pairs(g.evolve(G_NW, i)) for i in range(4)]
LWSSES_W = [to_pairs(g.evolve(LWSS_W, i)) for i in range(4)]
LWSSES_S = [to_pairs(g.evolve(LWSS_S, i)) for i in range(4)]

assert(all((0,0) in gl for gl in GLIDERS_SW))
assert(all((0,0) in gl for gl in GLIDERS_SE))
assert(all((0,0) in gl for gl in GLIDERS_NW))
assert(all((0,0) in lwss for lwss in LWSSES_W))
assert(all((0,0) in lwss for lwss in LWSSES_S))

def get_g0(lane):
    x = lane // 2 - 5
    glider = g.transform(G_NE, x, lane - x)
    return g.evolve(glider, 2 * (1 + lane % 2))

G1 = get_g0(LANE1)
G2 = get_g0(LANE2)

b64 = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789$#"

def coord_to_string(x, y):
    return b64[x & 63] + b64[y & 63] + b64[((x >> 6) & 7) + ((y >> 3) & 56)]

def canonical(cells):
    return "".join(sorted(coord_to_string(x, y) for x, y in to_pairs(cells)))

elbows = [False, "G", "F", "E", "D", False, False, False, False, "C", "B", "A",
          "Ar", "Br", "Cr", False, False, False, False, "Dr", "Er", "Fr", "Gr"]

def is_elbow(cells):
    # insist on 4 on cells
    if len(cells) != 8:
        return False
   
    # rule out tubs
    if max(cells[::2]) - min(cells[::2]) != 1:
        return False

    # work out the elbow type based on the value of the furthest NW lane
    min_l = min(cells[i] + cells[i+1] for i in range(0, len(cells), 2))

    return elbows[min_l + 11] if abs(min_l) <= 11 else False

def test(cells, lane):
    cells2 = g.evolve(cells, 4)
    if len(cells) != len(cells2):
        return 0, [], None

    sumx1, sumy1 = sum(cells[::2]), sum(cells[1::2])
    sumx2, sumy2 = sum(cells2[::2]), sum(cells2[1::2])

    delta = (sumx2 - sumx1, sumy2 - sumy1)

    for _ in range(4):
        cells2 = g.evolve(cells2, 4)
        sumx1, sumy1 = sumx2, sumy2
        sumx2, sumy2 = sum(cells2[::2]), sum(cells2[1::2])
        new_delta = (sumx2 - sumx1, sumy2 - sumy1)
        if new_delta != delta:
            return 0, [], None

# a,b,c,d,e are used to convert x, y values into a lane number and output type

    if delta == (0, 0):
        spaceships = []
#    elif delta == (-5, 5):
#        spaceships = GLIDERS_SW
#        a, b, c, d, e = 1, 1, -1, 0, 0
    elif delta == (5, 5):
        spaceships = GLIDERS_SE
        a, b, c, d, e = 1, -1, 1, 0, 1
    elif delta == (-5, -5):
        spaceships = GLIDERS_NW
        a, b, c, d, e = 1, -1, 2, 0, 2
#    elif delta == (-18, 0) or delta == (-24, 0):
#        spaceships = LWSSES_W
#        a, b, c, d, e = 0, 2, 0, 1, 3
#    elif delta == (0, 18) or delta == (0, 24):
#        spaceships = LWSSES_S
#        a, b, c, d, e = 2, 0, 0, 1, 4
    else:
        return 0, [], None

    pairs = to_pairs(cells)
    if spaceships and lane is None:
        found = False
        for x0, y0 in pairs:
            for phase, ss in enumerate(spaceships):
                if all((x0+i, y0+j) in pairs for (i, j) in ss):
                    for i, j in ss:
                        pairs.remove((x0+i, y0+j))
                    found = True
                    lane = a * x0 + b * y0 + c + d * (x0+y0)%2, e + 8 * phase
                    break
            if found:
                break

        if not found:
            return 0, [], None

        cells = []
        for x, y in pairs:
            cells.append(x)
            cells.append(y)

    sort = sorted(pairs)
    for p in range(2):
        cells = g.evolve(cells, 1)
        if sorted(to_pairs(cells)) == sort:
            return p + 1, cells, lane
       
    return 0, [], None

offset = 0

def show_it(recipe, lane, move, elbow_type, start_elbow):

    global offset

    start_cells, start_type, start_lane = start_elbow

    res = ""
    phase = 0
    if lane is not None:
        direction = lane[1] % 8
        phase = lane[1] // 8
        if direction == 1:
            res = "R%d" % (lane[0] - start_lane)
        elif direction == 2:
            res = "L%d" % (lane[0] - start_lane)
#        elif direction == 3:
#            res = "LWSS_W"
#        elif direction == 4:
#            res = "LWSS_S"

    if move is None:
        res += "k"
    else:
        res += "m%d%s%s" % (move - start_lane, start_type, elbow_type)

    g.putcells(make_text(res, "mono"), offset, -80)

    g.putcells(start_cells, offset, 0)

    for i, t in enumerate(recipe[::2]):
        if t is not None:
            d = 80*i + MAX_DIFF / 4 + 20
            g.putcells(g.evolve(G1, t + MAX_DIFF), offset-d, d)

    for i, t in enumerate(recipe[1::2]):
        if t is not None:
            d = 80*i + MAX_DIFF / 4 + 20
            g.putcells(g.evolve(G2, t + MAX_DIFF), offset-d, d)

    res += ": "

    for i in range(0, len(recipe), 2):
        if recipe[i] is None:
            res += "eo"[(recipe[i+1]+phase)%2] + "-9999 "
        elif recipe[i+1] is None:
            res += "eo"[(recipe[i]+phase)%2] + "9999 "
        else:
            res += "eo"[(recipe[i]+phase)%2] + str(recipe[i]-recipe[i+1]) + " "
           
    f.write(res + "\n")
    f.flush()

    offset += 100
    g.update()

def store(cells, lane, recipe, period, depth, next_pats):

    old_depth = -1

    canon = canonical(cells) + "%" + str(lane)
    if canon in depths:
        old_depth = depths[canon]
    elif period == 2:
        canon1 = canonical(g.evolve(cells, 1)) + "%" + str(lane)
        if canon1 in depths:
            old_depth = depths[canon1]

    if old_depth < depth:
        depths[canon] = depth
        if depth > 0:
            next_pats.append((cells, lane, recipe, period, depth))
        return True
    else:
        return False

def get_patterns(cells, period):

    if not cells:
        return

    # calculate where the gliders first hit the pattern
    min_lane = 99999
    for i in range(0, len(cells), 2):
        if LANE1 - 3 <= cells[i] + cells[i+1] <= LANE2 + 6:
            min_lane = min(min_lane, cells[i] - cells[i+1])

    if min_lane == 99999:
        return

    minx = min_lane // 2
    g1 = g.transform(G1, minx, -minx)
    g2 = g.transform(G2, minx, -minx)

    # Singletons
    for t in range(period):
        yield cells + g.evolve(g1, t), t, None
        yield cells + g.evolve(g2, t), None, t

    # Pairs
    for phase in range(period):
        yield cells + g1 + g2, phase, phase
        tg1 = g1 
        tg2 = g2
        for t in range(1, MAX_DIFF + 1):
            tg1 = g.transform(g.evolve(tg1, 3), -1, 1)
            tg2 = g.transform(g.evolve(tg2, 3), -1, 1)
            yield cells + g1 + tg2, phase, phase - t
            yield cells + tg1 + g2, phase - t, phase
        g1 = g.evolve(g1, 1)
        g2 = g.evolve(g2, 1)

def max_lane(cells):
    return max(cells[i] - cells[i+1] for i in range(0, len(cells), 2))

def search(elbow):

    global depths

    start_elbow = elbow, is_elbow(elbow), max_lane(elbow)

    #assume elbow is p1
    new_pats = [(elbow, None, (), 1, FULL_DEPTH)]
    depths = {}

    start = True

    iteration = 0

    while new_pats:
        iteration += 1
        next_pats = []
        n = 0
        for cells, lane, recipe, period, depth in new_pats:   
            g.show(str((start_elbow[1], iteration, n, len(new_pats))))
            n += 1

            # only fire stuff at an elbow at the very beginning
            if not start and is_elbow(cells):
                continue
       
            start = False

            for start_cells, t1, t2 in get_patterns(cells, period):
                
                end_cells = g.evolve(start_cells, GENS)
                
                if len(end_cells) > 2 * (MAX_POP[iteration-1] + 12):
                    continue
                
                new_period, end_cells, new_lane = test(end_cells, lane)
                
                if new_period == 0:
                    continue
                
                if len(end_cells) > 2 * MAX_POP[iteration-1]:
                    continue
   
                new_depth = depth - 1
                new_recipe = recipe + (t1, t2)

                if lane is None and new_lane is not None:
                    new_depth += CLEANUP_DEPTH

                if store(end_cells, new_lane, new_recipe, new_period, new_depth, next_pats):

#                   Elbow killing recipes     
#                   if new_lane is not None and not end_cells:
#                       show_it(new_recipe, new_lane, None, startelbow)
               
                    elbow = is_elbow(end_cells)
                    if elbow:
                        move = max_lane(end_cells)
                        show_it(new_recipe, new_lane, move, elbow, start_elbow)
       
        new_pats = next_pats

BLOCK = g.parse("2o$2o!")

ELBOWS = [BLOCK,
          g.transform(BLOCK, 0, -1),
          g.transform(BLOCK, 0, -2),
          g.transform(BLOCK, 0, -7),
          g.transform(BLOCK, 0, -8),
          g.transform(BLOCK, 0, -9),
          g.transform(BLOCK, 0, -10)]

# sanity check to make sure all elbows are distinct
elbow_types = set()

for elbow in ELBOWS:
    elbow_type = is_elbow(elbow)

    assert(elbow_type != False)
    assert(elbow_type.isupper())
    assert(elbow_type not in elbow_types)

    elbow_types.add(elbow_type)


#prof = open("/home/user/life/elbow.stats", "w")
#pr = cProfile.Profile()
#pr.enable()

# do it
f = open(OUTFILE, 'w')

g.new('')

for elbow in ELBOWS:
    search(elbow)

f.close()

#pr.disable()
#pstats.Stats(pr, stream=prof).sort_stats("cumulative").print_stats()
#prof.close()
