import numpy as np
import pandas as pd
from pulp import *

"""valeurs = {'restauration': [8000.0, 20000.0],
 'photo vidéo': [0.0, 100000.0],
 'artiste': [0.0, 180000.0],
 'décoration': [0.0, 50000.0],
 'salle': [0.0, 50000.0],
 'gateau': [1350.0, 2500.0]}"""
valeurs = {'restauration': [8000.0, 20000.0],
 'photo vidéo': [0.0, 100000.0],
 'artiste': [0.0, 180000.0],
 'décoration': [0.0, 50000.0],
 'salle': [0.0, 50000.0],
 'gateau': [1350.0, 2500.0]}


def opt(budget, choix, vals=[10, 6]):
    for i in valeurs:
        if i not in choix:
            valeurs[i] = [0, 0]

    # valeurs['nombre de personnes'] = [vals[0], vals[0]]
    # valeurs['part'] = [vals[1], vals[1]]

    # Initialiser les variables
    # variables = [LpVariable(i, lowBound=0, cat=LpInteger) for i in valeurs.keys()]

    pu = LpVariable("pu", lowBound=0, cat=LpInteger)
    # n = LpVariable("n", lowBound=0, cat=LpInteger)
    pv = LpVariable("pv", lowBound=0, cat=LpInteger)
    art = LpVariable("art", lowBound=0, cat=LpInteger)
    deco = LpVariable("deco", lowBound=0, cat=LpInteger)
    sal = LpVariable("sal", lowBound=0, cat=LpInteger)
    prx = LpVariable("prx", lowBound=0, cat=LpInteger)
    # prt = LpVariable("prt", lowBound=0, cat=LpInteger)

    # Initialiser le problème
    probleme = LpProblem(name='Répartition budget', sense=LpMaximize)
    # Ajouter la fonction objectif à maximiser au problème
    fonction_objectif = LpAffineExpression(e=pu * vals[0] + pv + art + deco + sal + prx * vals[1])
    probleme.setObjective(fonction_objectif)

    # Ajouter contraintes budgéétaire
    # print(f'Variables : {variables}')
    contrainte_budget = LpConstraint(e=pu * vals[0] + pv + art + deco + sal + prx * vals[1], sense=LpConstraintEQ,
                                     name='contrainte_budgétaire', rhs=budget)
    probleme.add(contrainte_budget)

    contrainte = LpConstraint(e=pu, sense=LpConstraintGE, name='great contrainte ' + 'restauration',
                              rhs=valeurs['restauration'][0])
    probleme.add(contrainte)
    contrainte_ = LpConstraint(e=pu, sense=LpConstraintLE, name='less contrainte ' + 'restauration',
                               rhs=valeurs['restauration'][1])
    probleme.add(contrainte_)

    contrainte = LpConstraint(e=pv, sense=LpConstraintGE, name='great contrainte ' + 'photo vidéo',
                              rhs=valeurs['photo vidéo'][0])
    probleme.add(contrainte)
    contrainte_ = LpConstraint(e=pv, sense=LpConstraintLE, name='less contrainte ' + 'photo vidéo',
                               rhs=valeurs['photo vidéo'][1])
    probleme.add(contrainte_)

    """contrainte = LpConstraint(e=n, sense=LpConstraintGE, name='great contrainte ' + 'nombre de personnes', rhs=valeurs['nombre de personnes'][0])
    probleme.add(contrainte)            
    contrainte_ = LpConstraint(e=n, sense=LpConstraintLE, name='less contrainte ' + 'nombre de personnes', rhs=valeurs['nombre de personnes'][1])
    probleme.add(contrainte_)"""

    contrainte = LpConstraint(e=art, sense=LpConstraintGE, name='great contrainte ' + 'artiste',
                              rhs=valeurs['artiste'][0])
    probleme.add(contrainte)
    contrainte_ = LpConstraint(e=art, sense=LpConstraintLE, name='less contrainte ' + 'artiste',
                               rhs=valeurs['artiste'][1])
    probleme.add(contrainte_)

    contrainte = LpConstraint(e=deco, sense=LpConstraintGE, name='great contrainte ' + 'décoration',
                              rhs=valeurs['décoration'][0])
    probleme.add(contrainte)
    contrainte_ = LpConstraint(e=deco, sense=LpConstraintLE, name='less contrainte ' + 'décoration',
                               rhs=valeurs['décoration'][1])
    probleme.add(contrainte_)

    contrainte = LpConstraint(e=sal, sense=LpConstraintGE, name='great contrainte ' + 'salle', rhs=valeurs['salle'][0])
    probleme.add(contrainte)
    contrainte_ = LpConstraint(e=sal, sense=LpConstraintLE, name='less contrainte ' + 'salle', rhs=valeurs['salle'][1])
    probleme.add(contrainte_)

    contrainte = LpConstraint(e=prx, sense=LpConstraintGE, name='great contrainte ' + 'gateau', rhs=valeurs['gateau'][0])
    probleme.add(contrainte)
    contrainte_ = LpConstraint(e=prx, sense=LpConstraintLE, name='less contrainte ' + 'gateau', rhs=valeurs['gateau'][1])
    probleme.add(contrainte_)

    """contrainte = LpConstraint(e=prt, sense=LpConstraintGE, name='great contrainte ' + 'part', rhs=valeurs['part'][0])
    probleme.add(contrainte)            
    contrainte_ = LpConstraint(e=prt, sense=LpConstraintLE, name='less contrainte ' + 'part', rhs=valeurs['part'][1])
    probleme.add(contrainte_)"""
    # Initialiser le solveur
    solver = PULP_CBC_CMD(timeLimit=20, msg=True)
    probleme.solve(solver=solver)

    repartitions = {
        "Artiste": art.value(), "Décoration": deco.value(), "Photos Vidéos": pv.value(),
        "Restauration": {"Prix Unitaire": pu.value(), "Invités": vals[0], "Prix total": pu.value() * vals[0]},
        "Salle": sal.value(),
        "Gâteau": {"Prix Unitaire": prx.value(), "Parts": vals[1], "Prix total": prx.value() * vals[1]}
    }

    # print(probleme)
    return repartitions
