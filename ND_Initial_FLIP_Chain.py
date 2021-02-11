# -*- coding: utf-8 -*-
"""
Run simple Flip chain on ND precincts
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

trimmed_graph = Graph.from_json("./ND_Precincts_trimmed.json")


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

for n in trimmed_graph.nodes():
    totpop += trimmed_graph.nodes[n]["POP10"]
 
ideal_pop = totpop/num_districts
    
cddict_trimmed =  recursive_tree_part(trimmed_graph,range(num_districts),ideal_pop,"POP10", .02,1)


initial_flip_part = Partition(trimmed_graph, cddict_trimmed, updaters)


compactness_bound = constraints.UpperBound(
    lambda p: len(p["cut_edges"]), 2 * len(initial_flip_part["cut_edges"])
)

flip_chain = MarkovChain(
    proposal=propose_random_flip,
    constraints=[
        constraints.within_percent_of_ideal_population(initial_flip_part, 0.05), constraints.single_flip_contiguous, compactness_bound
    ],
    accept=accept.always_accept,
    initial_state=initial_flip_part,
    total_steps=10000
)





newdir = "./Outputs/Flip/"
os.makedirs(os.path.dirname(newdir + "init.txt"), exist_ok=True)
with open(newdir + "init.txt", "w") as f:
    f.write("Created Folder")
    

plot_df['current'] = plot_df.index.map(cddict_trimmed)
plot_df.plot(column='current',cmap='tab20')
plt.savefig(newdir+"Initial_plan.png")
plt.close()


t = 0

mms_flip = [[],[],[]]
egs_flip = [[],[],[]]
hmss_flip = [[],[],[]]
ces_flip = []
for part in flip_chain:
    
    
    ces_flip.append(len(part['cut_edges']))   
    

    for elect in range(num_elections):
        mms_flip[elect].append(mean_median(part[election_names[elect]]))
        egs_flip[elect].append(efficiency_gap(part[election_names[elect]]))
        hmss_flip[elect].append(part[election_names[elect]].wins("D"))
    
    t+=1
    if t%1000 == 0:
        plot_df['current'] = plot_df.index.map(dict(part.assignment))
        plot_df.plot(column='current',cmap='tab20')
        plt.savefig(newdir+f"Step_{t}.png")
        plt.close()


for i in range(num_elections):
    plt.figure()
    plt.suptitle(election_names[i])
    plt.subplot(2,2,1)
    plt.plot(ces_flip)
    plt.title("Cut Edges")
    
    
    
    plt.subplot(2,2,2)
    plt.plot(mms_flip[i])
    plt.title("Mean Median ")
    
    
    plt.subplot(2,2,3)
    plt.plot(egs_flip[i])
    plt.title("Efficiency Gap")
    
    
    plt.subplot(2,2,4)
    plt.plot(hmss_flip[i])
    plt.title("Seats")
    
    
    plt.tight_layout()
    plt.savefig(newdir+f'Traces_{election_names[i]}.png')
    plt.close()

for i in range(num_elections):
    plt.figure()
    plt.suptitle(election_names[i])

    plt.subplot(2,2,1)
    plt.hist(ces_flip)
    plt.title("Cut Edges")
    
    
    
    plt.subplot(2,2,2)
    plt.hist(mms_flip[i])
    plt.title("Mean Median ")
    
    
    plt.subplot(2,2,3)
    plt.hist(egs_flip[i])
    plt.title("Efficiency Gap")
    
    
    plt.subplot(2,2,4)
    plt.hist(hmss_flip[i])
    plt.title("Seats")
    
    
    plt.tight_layout()
    plt.savefig(newdir+f'Hists_{election_names[i]}.png')
    plt.close()


