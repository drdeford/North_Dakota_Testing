

# -*- coding: utf-8 -*-
"""
Run simple ReCom chain on ND precincts
"""

import csv
import os
from functools import partial
import json

import geopandas as gpd
import matplotlib.pyplot as plt

from gerrychain import (
    Election,
    Graph,
    MarkovChain,
    Partition,
    accept,
    constraints,
    updaters,
)
from gerrychain.metrics import efficiency_gap, mean_median
from gerrychain.proposals import recom, propose_random_flip
from gerrychain.updaters import cut_edges
from gerrychain.tree import recursive_tree_part




plot_df = gpd.read_file("./Shapefiles/ND_Precincts/nd_2016.shp")

dual_graph = Graph.from_json("./ND_Precincts.json")


num_elections = 3
num_districts = 4


election_names = [
    "PRES16",
    "SEN16",
    "GOV16",
]
election_columns = [
    ['G16PRERTRU', 'G16PREDCLI'],
    ["G16USSRHOE", "G16USSDGLA"],
    ["G16GOVRBUR", "G16GOVDNEL"],
]

updaters = {
    "population": updaters.Tally("POP10", alias="population"),
    "cut_edges": cut_edges,
}

elections = [
    Election(
        election_names[i],
        {"R": election_columns[i][0], "D": election_columns[i][1]},
    )
    for i in range(num_elections)
]

election_updaters = {election.name: election for election in elections}

updaters.update(election_updaters)


    
totpop = 0

for n in dual_graph.nodes():
    totpop += dual_graph.nodes[n]["POP10"]
 
ideal_pop = totpop/num_districts
    
cddict =  recursive_tree_part(dual_graph,range(num_districts),ideal_pop,"POP10", .02,1)



initial_recom_part = Partition(dual_graph, cddict, updaters)

tree_proposal = partial(recom, pop_col="POP10", pop_target=ideal_pop, epsilon=0.02, node_repeats=1)



recom_chain = MarkovChain(
    proposal=tree_proposal,
    constraints=[
        constraints.within_percent_of_ideal_population(initial_recom_part, 0.05),
    ],
    accept=accept.always_accept,
    initial_state=initial_recom_part,
    total_steps=100
)



newdir = "./Outputs/ReCom/"
os.makedirs(os.path.dirname(newdir + "init.txt"), exist_ok=True)
with open(newdir + "init.txt", "w") as f:
    f.write("Created Folder")
    

plot_df['current'] = plot_df.index.map(cddict)
plot_df.plot(column='current',cmap='tab20')
plt.savefig(newdir+"Initial_plan.png")
plt.close()


t = 0

mms_recom = [[],[],[]]
egs_recom = [[],[],[]]
hmss_recom = [[],[],[]]
ces_recom = []
for part in recom_chain:
    
    
    ces_recom.append(len(part['cut_edges']))   
    

    for elect in range(num_elections):
        mms_recom[elect].append(mean_median(part[election_names[elect]]))
        egs_recom[elect].append(efficiency_gap(part[election_names[elect]]))
        hmss_recom[elect].append(part[election_names[elect]].wins("D"))
    
    t+=1
    if t%10 == 0:
        plot_df['current'] = plot_df.index.map(dict(part.assignment))
        plot_df.plot(column='current',cmap='tab20')
        plt.savefig(newdir+f"Step_{t}.png")
        plt.close()


for i in range(num_elections):
    plt.figure()
    plt.suptitle(election_names[i])
    plt.subplot(2,2,1)
    plt.plot(ces_recom)
    plt.title("Cut Edges")
    
    
    
    plt.subplot(2,2,2)
    plt.plot(mms_recom[i])
    plt.title("Mean Median ")
    
    
    plt.subplot(2,2,3)
    plt.plot(egs_recom[i])
    plt.title("Efficiency Gap")
    
    
    plt.subplot(2,2,4)
    plt.plot(hmss_recom[i])
    plt.title("Seats")
    
    
    plt.tight_layout()
    plt.savefig(newdir+f'Traces_{election_names[i]}.png')
    plt.close()

for i in range(num_elections):
    plt.figure()
    plt.suptitle(election_names[i])

    plt.subplot(2,2,1)
    plt.hist(ces_recom)
    plt.title("Cut Edges")
    
    
    
    plt.subplot(2,2,2)
    plt.hist(mms_recom[i])
    plt.title("Mean Median ")
    
    
    plt.subplot(2,2,3)
    plt.hist(egs_recom[i])
    plt.title("Efficiency Gap")
    
    
    plt.subplot(2,2,4)
    plt.hist(hmss_recom[i])
    plt.title("Seats")
    
    
    plt.tight_layout()
    plt.savefig(newdir+f'Hists_{election_names[i]}.png')
    plt.close()




