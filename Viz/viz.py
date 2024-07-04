import networkx as nx
import matplotlib.pyplot as plt
from pyvis.network import Network
import plotly.graph_objects as go

class NetworkVisualization:
    def __init__(self):
        self.graph = nx.DiGraph()

    def add_agent(self, agent_id, agent_type):
        print(f"Adding agent {agent_id} of type {agent_type}")
        self.graph.add_node(agent_id, label=f"{agent_type} {agent_id}")

    def add_connection(self, from_agent, from_port_name, to_agent, to_port_name):
        print(f"Adding connection from {from_agent} ({from_port_name}) to {to_agent} ({to_port_name})")
        self.graph.add_edge(from_agent, to_agent, label=f'{from_port_name} -> {to_port_name}')

    def draw_network(self):
        pos = nx.spring_layout(self.graph)

        edge_x = []
        edge_y = []
        for edge in self.graph.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_x.append(x0)
            edge_x.append(x1)
            edge_x.append(None)
            edge_y.append(y0)
            edge_y.append(y1)
            edge_y.append(None)

        edge_trace = go.Scatter(
            x=edge_x, y=edge_y,
            line=dict(width=0.5, color='#888'),
            hoverinfo='none',
            mode='lines')

        node_x = []
        node_y = []
        node_labels = []
        for node in self.graph.nodes():
            x, y = pos[node]
            node_x.append(x)
            node_y.append(y)
            node_labels.append(self.graph.nodes[node]['label'])

        node_trace = go.Scatter(
            x=node_x, y=node_y,
            mode='markers+text',
            text=node_labels,
            textposition="top center",
            hoverinfo='text',
            marker=dict(
                showscale=True,
                colorscale='YlGnBu',
                size=10,
                colorbar=dict(
                    thickness=15,
                    title='Node Connections',
                    xanchor='left',
                    titleside='right'
                )
            )
        )

        fig = go.Figure(data=[edge_trace, node_trace],
                        layout=go.Layout(
                            title='IoT Network Visualization',
                            titlefont_size=16,
                            showlegend=False,
                            hovermode='closest',
                            margin=dict(b=20,l=5,r=5,t=40),
                            annotations=[dict(
                                text="",
                                showarrow=False,
                                xref="paper", yref="paper"
                            )],
                            xaxis=dict(showgrid=False, zeroline=False),
                            yaxis=dict(showgrid=False, zeroline=False))
                        )
        fig.show()