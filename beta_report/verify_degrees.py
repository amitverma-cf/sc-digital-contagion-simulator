import pandas as pd
import networkx as nx
import json

# Load the network and get degrees
with open('analysis/social_network.graphml') as f:
    G = nx.read_graphml(f)

# Get degrees for the targeting strategy agents
influencer_agents = [32, 59, 66, 78, 85]
random_agents = [14, 16, 30, 34, 78]
isolated_agents = [41, 83, 94, 96, 98]

def get_avg_degree(agent_list):
    degrees = []
    for agent_id in agent_list:
        try:
            degree = G.degree(str(agent_id))
            degrees.append(degree)
        except:
            print(f"  Agent {agent_id} not found in graph!")
    return degrees

print('AGENT DEGREES FROM NETWORK:')
print(f'\nTop Influencers {influencer_agents}:')
degrees = get_avg_degree(influencer_agents)
print(f'  Degrees: {degrees}')
print(f'  Average: {sum(degrees)/len(degrees):.1f}')

print(f'\nRandom {random_agents}:')
degrees = get_avg_degree(random_agents)
print(f'  Degrees: {degrees}')
print(f'  Average: {sum(degrees)/len(degrees):.1f}')

print(f'\nIsolated {isolated_agents}:')
degrees = get_avg_degree(isolated_agents)
print(f'  Degrees: {degrees}')
print(f'  Average: {sum(degrees)/len(degrees):.1f}')

# Compare with report claims
print('\n\nREPORT TABLE 3 vs ACTUAL DEGREES:')
print('Report claims for TOP INFLUENCERS: Avg Degree 10.8')
degrees = get_avg_degree(influencer_agents)
print(f'Actual: {sum(degrees)/len(degrees):.1f}')

print('\nReport claims for RANDOM: Avg Degree 5.4')
degrees = get_avg_degree(random_agents)
print(f'Actual: {sum(degrees)/len(degrees):.1f}')

print('\nReport claims for ISOLATED: Avg Degree 2.0')
degrees = get_avg_degree(isolated_agents)
print(f'Actual: {sum(degrees)/len(degrees):.1f}')
