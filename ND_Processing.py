# -*- coding: utf-8 -*-
"""
Add population to ND precinct shapefile and write out corresponding json dual graph
Remove doughnut precincts
"""

import geopandas as gpd
import maup
from gerrychain import Graph
import networkx as nx
import matplotlib.pyplot as plt


blocks = gpd.read_file("./Shapefiles/ND_Blocks/tabblock2010_38_pophu.shp")
precincts = gpd.read_file("./Shapefiles/ND_Precincts/nd_2016.shp")

assignment = maup.assign(blocks, precincts)

precincts["POP10"] = blocks["POP10"].groupby(assignment).sum()
precincts['C_X'] = precincts.centroid.x
precincts['C_Y'] = precincts.centroid.y

dual_graph = Graph.from_geodataframe(precincts)

dual_graph.add_data(precincts)

dual_graph.to_json("./ND_Precincts.json")


plt.figure()
nx.draw(dual_graph, pos={n:(dual_graph.nodes[n]['C_X'],dual_graph.nodes[n]['C_Y']) for n in dual_graph.nodes()}, node_color = [dual_graph.nodes[n]['G16PRERTRU']/(dual_graph.nodes[n]['G16PRERTRU']+dual_graph.nodes[n]['G16PREDCLI']) for n in dual_graph.nodes()]
, cmap = 'coolwarm', node_size=30)
plt.savefig("./Outputs/ND_Dual_Graph.png")
plt.close()


#remove donuts

cols = ['G16PRERTRU',
'G16PREDCLI',
'G16PRELJOH',
'G16PREGSTE',
'G16PRECCAS',
'G16PREOFUE',
'G16PREOWRI',
'G16USSRHOE',
'G16USSDGLA',
'G16USSLMAR',
'G16USSIGER',
'G16USSOWRI',
'G16HALRCRA',
'G16HALDIRO',
'G16HALLSEA',
'G16HALOWRI',
'G16GOVRBUR',
'G16GOVDNEL',
'G16GOVLRIS',
'G16GOVOWRI',
'G16AUDRGAL',
'G16AUDLRIE',
'G16AUDOWRI',
'G16TRERSCH',
'G16TREDMAT',
'G16TRELOLS',
'G16TREOWRI',
'G16INSRGOD',
'G16INSDBUF',
'G16INSLBAT',
'G16INSOWRI',
'G16PSCRFED',
'G16PSCDHUN',
'G16PSCLSKA',
'G16PSCOWRI',
'area',
'POP10']

trimmed_graph = dual_graph.copy()

degrees = nx.degree(dual_graph)

for node in dual_graph.nodes():
    if degrees[node] == 1 and dual_graph.nodes[node]['boundary_node'] == False:
        trimmed_graph.remove_node(node)
        target = list(dual_graph[node].keys())[0]
        for col in cols:
        
            trimmed_graph.nodes[target][col] += dual_graph.nodes[node][col]
    

trimmed_graph.to_json("./ND_Precincts_trimmed.json")

plt.figure()
nx.draw(trimmed_graph, pos={n:(trimmed_graph.nodes[n]['C_X'],trimmed_graph.nodes[n]['C_Y']) for n in trimmed_graph.nodes()}, node_color = [trimmed_graph.nodes[n]['G16PRERTRU']/(trimmed_graph.nodes[n]['G16PRERTRU']+trimmed_graph.nodes[n]['G16PREDCLI']) for n in trimmed_graph.nodes()]
, cmap = 'coolwarm', node_size=30)
plt.savefig("./Outputs/ND_Dual_Graph_trimmed.png")
plt.close()

