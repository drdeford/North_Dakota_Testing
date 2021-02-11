# North_Dakota_Testing

This repository contains some initial scripts and data needed to get started building districting ensembles on the precincts of North Dakota. The underlying precinct data was prepared by the <a href ="https://dataverse.harvard.edu/dataverse/electionscience">Voting and Election Science Team</a> and can be download from the Harvard Dataverse <a href ="https://dataverse.harvard.edu/file.xhtml?persistentId=doi:10.7910/DVN/NH5S2I/JM0M6V"> here</a> [1]. The block level population data was downloaded from the US Census <a href="https://www.census.gov/geographies/mapping-files/2010/geo/tiger-data.html"> website</a>. Versions of these files are stored in the Shapefiles directory. 

## Processing

The ND_Processing.py script prepares the necessary dual graphs from the shapefiles. The specifics steps are: 

1. Load in the shapefiles as geodataframes using the geopandas package.
2. Use the <https://github.com/mggg/maup>MAUP</a> package to aggregate the population totals from the blocks to the precincts.
3. Create the initial dual graph of the precincts and attach the voting and population column data. This is the ND_Precincts.json file in the main repository. 
4. Make a plot of the graph as a sanity check of the process (nodes colored by 2016 presidential election proportions):

![ND Dual Graph](https://raw.githubusercontent.com/drdeford/North_Dakota_Testing/main/Outputs/ND_Dual_Graph.png)
5. Since there are doughnut precincts (i.e. precincts that are wholly contained in another precinct) the FLIP chain will be obstructed if we attempt to use the previous dual graph. Thus, we next make a smaller "trimmed" dual graph where the doughnuts and their population/vote totals are aggregated into the surrounding precinct. 
6. This trimmed version is saved as the ND_Precincts_trimmed.json file in the main repository. 

## Chain Runs
There are two scripts for actual using the <https://github.com/mggg/gerrychain>GerryChain</a> package to generate an ensemble of plans using the dual graphs created by the processing script. Since this is just a test, the state is partitioned into just 4 pieces, rather then the 47 current districts. Each script corresponds to a different proposal method. The ND_Initial_FLIP_Chain.py version uses the single node flip proposal, while the ND_Initial_RECOM_Chain.py uses a version of the spanning tree ReCombination propsal introduced in [2].  Each script sets up the necessary updaters, constraints, and proposal functions and then makes a short (10,000 step and 100 step) run of the Markov chain, starting from a random seed.  At each step of each chain some partisan statistics using two-party election data from the 2016 presidential, senatorial, and gubernatorial races are recorded. Figures showing some intermediate states of the Markov chains and summary statistics at the end of the run are automatically written out to the outputs file. 


## References
[1] Voting and Election Science Team, 2018, "2016 Precinct-Level Election Results", https://doi.org/10.7910/DVN/NH5S2I, Harvard Dataverse, V52 

[2] D. DeFord, M. Duchin, and J. Solomon, ReCombination: A family of Markov chains for redistricting, <a href ="https://arxiv.org/abs/1911.05725">arXiv:1911.05725<a/>, (2019). 

