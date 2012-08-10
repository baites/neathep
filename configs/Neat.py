# Neat.py
#
# Developers:
#   Victor Eduardo Bazterra 2010 (UIC)
#   Phillip Eller 2010 (ETH) 
#   Christfried Focke 2010 (ETH) 
#
# Descrition:
#   Main configuration file for neat

# Phenotype

max_weight = 5
min_weight = -5
feedforward = 1
nn_activation = 'sigmoid' 
hidden_nodes = 0
weight_stdev = 0.12
fully_connected = 1

# Genetic 

pop_size = 200 
max_fitness_threshold = 1 
prob_addconn = 0.5
prob_addnode = 0.5
prob_mutatebias = 0.2
bias_mutation_power = 0.5 
prob_mutate_weight = 0.9 
weight_mutation_power = 0.01 
prob_togglelink = 0.02 
elitism = 1 

# Genotype compatibility

compatibility_threshold = 23.0
compatibility_change = 0.0
excess_coeficient = 1.0
disjoint_coeficient = 1.0
weight_coeficient = 1.0

# Species

species_size = 10
survival_threshold = 0.12
old_threshold = 30
youth_threshold = 10
old_penalty = 0.2
youth_boost = 1.2
max_stagnation = 15
