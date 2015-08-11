#!/usr/bin/python

# Copyright 2014, Gurobi Optimization, Inc.

# Solve a traveling salesman problem on a randomly generated set of
# points using lazy constraints.   The base MIP model only includes
# 'degree-2' constraints, requiring each node to have exactly
# two incident edges.  Solutions to this model may contain subtours -
# tours that don't visit every city.  The lazy constraint callback
# adds new constraints to cut them off.

import math
import StringIO
from gurobipy import *


# Callback - use lazy constraints to eliminate sub-tours

def subtourelim(model, where):
    if where == GRB.callback.MESSAGE:
        print >>model.__output, model.cbGet(GRB.callback.MSG_STRING),

    if where == GRB.callback.MIPSOL:
        selected = []
        n = model._n
        # make a list of edges selected in the solution
        for i in range(n):
            sol = model.cbGetSolution([model._vars[i,j] for j in range(n)])
            selected += [(i,j) for j in range(n) if sol[j] > 0.5]
        # find the shortest cycle in the selected edge list
        tour = subtour(selected,n)
        if len(tour) < n:
            # add a subtour elimination constraint
            expr = 0
            for i in range(len(tour)):
                for j in range(i+1, len(tour)):
                    expr += model._vars[tour[i], tour[j]]
            model.cbLazy(expr <= len(tour)-1)


# Euclidean distance between two points

def distance(points, i, j):
    dx = points[i][0] - points[j][0]
    dy = points[i][1] - points[j][1]
    return math.sqrt(dx*dx + dy*dy)


# Given a list of edges, finds the shortest subtour

def subtour(edges, n):
    visited = [False]*n
    cycles = []
    lengths = []
    selected = [[] for i in range(n)]
    for x,y in edges:
        selected[x].append(y)
    while True:
        current = visited.index(False)
        thiscycle = [current]
        while True:
            visited[current] = True
            neighbors = [x for x in selected[current] if not visited[x]]
            if len(neighbors) == 0:
                break
            current = neighbors[0]
            thiscycle.append(current)
        cycles.append(thiscycle)
        lengths.append(len(thiscycle))
        if sum(lengths) == n:
            break
    return cycles[lengths.index(min(lengths))]


def optimize(points, output=False):
    n = len(points)
    m = Model()

    if not output:
        m.params.OutputFlag = 0

    m.setParam('TimeLimit', 10)

    # Create variables

    vars = {}
    for i in range(n):
        for j in range(i+1):
            vars[i,j] = m.addVar(obj=distance(points, i, j), vtype=GRB.BINARY,
                                 name='e'+str(i)+'_'+str(j))
            vars[j,i] = vars[i,j]
    m.update()


    # Add degree-2 constraint, and forbid loops

    for i in range(n):
        m.addConstr(quicksum(vars[i,j] for j in range(n)) == 2)
        vars[i,i].ub = 0
    m.update()


    # Optimize model

    m._vars = vars
    m._n = n
    m.params.LazyConstraints = 1

    output = StringIO.StringIO()
    m.__output = output

    m.optimize(subtourelim)

    if (m.status != 2):
        return ["error"]

    solution = m.getAttr('x', vars)
    selected = [(i,j) for i in range(n) for j in range(n) if solution[i,j] > 0.5]

    assert len(subtour(selected,n)) == n

    return [subtour(selected,n), output.getvalue()]

points = [[28, 100], [152, 190], [400, 50], [138, 213.875], [192, 213.875], [325, 151.875], [264, 281.875], [111, 304.875], [84, 226.875], [160, 89.875], [264, 155.875]]
[[28, 100], [152, 190], [400, 50], [138, 213.875], [192, 213.875], [325, 151.875], [264, 281.875], [111, 304.875], [84, 226.875], [160, 89.875], [264, 155.875]]


def handleoptimize(jsdict):
    if 'vertices' in jsdict:
        tour = optimize(jsdict['vertices'])
        return {'tour': tour }

if __name__ == '__main__':
    import json
    jsdict = json.load(sys.stdin)
    jsdict = handleoptimize(jsdict)
    print 'Content-Type: application/json\n\n'
    print json.dumps(jsdict)
