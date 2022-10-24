import numpy as np
import pandas as pd
from pulp import *

def read_data(file, sep=",", header=0) -> pd.DataFrame:
    try:
        data = pd.read_excel(file, header=[header])
    except:
        try:
            data = pd.read_csv(file, encoding="ISO-8859-1", sep=sep)
        except Exception as e:
            print(e)
    return data

def clean_data(df: pd.DataFrame, col) -> pd.DataFrame:
    df.iloc[:,0] =  pd.Series(df.iloc[:,0]).fillna(method='ffill')
    df = df.drop_duplicates().apply(lambda x: x.astype(str).str.lower())
    df = df[(df[col] != "nan") & (df[col] != "#value!")]
    return df.apply(lambda x: x.str.strip())

def get_palier(df:pd.DataFrame, valeur:float) -> str:
    
    paliers = df.iloc[-1:,2:].transpose().astype('float')
    
    if(valeur > paliers.iloc[-1,0]):
            prev_ = next_ = paliers.index[-1]
            #next_ = paliers.index[-1]
            
    elif(valeur < paliers.iloc[0,0]):
            prev_ = next_ = paliers.index[0]
            #next_ = paliers.index[0]
            
    else:
        #prev_ = paliers.index[paliers.iloc[:,0]>=valeur][0]
        #next_ = paliers.index[paliers.iloc[:,0]>=valeur][1]
        prev_ = paliers.index[paliers.iloc[:,0]<=valeur][-1]
        next_ = paliers.index[paliers.iloc[:,0]>valeur][0]
        
    return prev_, next_

def choix_categ(df: pd.DataFrame, choix: list) -> dict:
    all_choice = df.iloc[:,1].unique().tolist()
    choices = [x.lower().strip() for x in choix]
    choix_possibles = list(set(all_choice) & set(choices))
    return {"X"+str(i+1): choix_possibles[i] for i in range(len(choix_possibles))}

def constraints(df: pd.DataFrame, budget: int, choice: list, invites: int) -> dict:
    prev_, next_ = get_palier(df, budget)
    #print(palier)
    contraintes = {}
    choix = choix_categ(df, choice)

    for it, elt in list(choix.items()):
        minim = float(df[df.iloc[:,1] == elt][prev_])
        maxim = float(df[df.iloc[:,1] == elt][next_])
        #categ = df[df.iloc[:,1] == elt].iloc[:,0]
        contraintes[elt] = [minim, maxim]
        #print(categ)


    return contraintes


def optimize(df:pd.DataFrame, budget: int, choice: list, invites: int) -> dict:
 
    contraintes = constraints(df, budget, choice, invites)
    choix = choix_categ(df,choice)
    
    # Initialiser les variables
    variables = [LpVariable(i, lowBound=0, cat=LpInteger) for i in choix.keys()]
    
    # Initialiser le problème
    probleme = LpProblem(name='Répartition budget', sense=LpMaximize)
    # Ajouter la fonction objectif à maximiser au problème
    fonction_objectif = LpAffineExpression(e=lpSum(variables))
    probleme.setObjective(fonction_objectif)

    # Ajouter contraintes budgéétaire
    contrainte_budget = LpConstraint(e=sum(variables), sense=LpConstraintEQ, name='contrainte_budgétaire', rhs=budget)
    probleme.add(contrainte_budget)

    for elt in variables:
        #Ajouter contrainte d'inégalités
        valeur_min = contraintes[choix[elt.name]][0]
        valeur_max = contraintes[choix[elt.name]][1]
        
        contrainte = LpConstraint(e=elt, sense=LpConstraintGE, name='great contrainte ' + choix[elt.name], rhs=valeur_min)
        probleme.add(contrainte)
            
        contrainte_ = LpConstraint(e=elt, sense=LpConstraintLE, name='less contrainte ' + choix[elt.name], rhs=valeur_max)
        probleme.add(contrainte_)


    # Initialiser le solveur
    solver = PULP_CBC_CMD(timeLimit=20, msg=True)
    probleme.solve(solver=solver)

    #print(probleme)
    repartitions = {}
    for val in variables:
        repartitions[choix[val.name]] = round(val.value())
    repartitions["Autres"] = budget - sum(repartitions.values())
    return repartitions

def optimize_min(df:pd.DataFrame, budget: int, choice: list, invites: int) -> dict:
    contraintes = constraints(df, budget, choice, invites)
    choix = choix_categ(df,choice)
    
    valeurs = ["alimentation", "ésthétique", "habillement", "média", "salle et déco",
               "accessoire", "plus", "cultures", "voyage lune de miel"]
    
    # Initialiser les variables
    ctes = [list(contraintes.values())[i][0] for i in range(len(list(choix.values())))]

    categ = df[df.iloc[:,1]==list(choix.values())[0]].iloc[0,0]
    total = 0
    all_vals = []
    
    for key, elt in contraintes.items():
        categ = df[df.iloc[:,1]==key].iloc[0,0]
        all_vals.append((categ, key, elt[0]))
        
    vals = [i for i in all_vals if i[0]=="alimentation"]
    vals.extend([i for i in all_vals if i[0]=="ésthétique" or i[0]=="habillement"])
    vals.extend([i for i in all_vals if i[0]=="média"])
    vals.extend([i for i in all_vals if i[0]=="salle et déco"])
    vals.extend([i for i in all_vals if i[0]=="accessoire"])
    vals.extend([i for i in all_vals if i[0]=="plus"])
    vals.extend([i for i in all_vals if i[0]=="cultures"])
    vals.extend([i for i in all_vals if i[0]=="voyage lune de miel"])
    
    repartitions = {}
    i = 0
    while (sum(repartitions.values()) < budget) and (i < len(vals)):
        if(sum(repartitions.values()) + vals[i][2]) <= budget:
            repartitions[vals[i][1]] = vals[i][2]
        else:
            repartitions[vals[i][1]] = 0
            
        i += 1

    repartitions["Autres"] = budget - sum(repartitions.values())
    return repartitions

def pulp_optimize(df:pd.DataFrame, budget: int, choice: list, invites: int) -> dict:
    if(budget < float(df.iloc[-1,2])):
        return optimize_min(df, budget, choice, invites)
    else :
        return optimize(df, budget, choice, invites)
