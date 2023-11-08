"""
visualization_networkx.py
--------------------
Visualization routine to plot the input graph and the coarse grained version side by side (using networkx)

author: Gabriele Di Bona
email: gabriele.dibona.work@gmail.com
"""

import matplotlib.pyplot as plt
import numpy as np
import matplotlib as mpl
import networkx as nx

def visualize_micro_macro(
    G_micro, mapping, G_macro,
    min_ns=60, max_ns=300, min_lw=2, max_lw=4, 
    ec='.7', nc='w', nec='steelblue',
    all_colorful=True, node_cmap='Set2',
    method_title = None,
):
    """
    Visualize microscale and macroscale networks side by side.

    Parameters:
    - G_micro (nx.Graph): Microscale network (a NetworkX graph).
    - G_macro (nx.Graph): Macroscale network (a NetworkX graph).
    - mapping (pd.DataFrame with columns 'micro' and 'macro'): dataframe with the mapping between nodes in the microscale and macroscale (original graph and coarse grained graph)
    - min_ns (int, optional): Minimum lode size for visualization. Default is 50.
    - max_ns (int, optional): Maximum node size for visualization. Default is 200.
    - min_lw (float, optional): Minimum linewidth for edges. Default is 1.5.
    - max_lw (float, optional): Maximum linewidth for edges. Default is 6.
    - ec (str, optional): Edge color. Default is '.5' (gray).
    - nc (str, optional): Node color. Default is 'w' (white).
    - nec (str, optional): Node edge color. Default is 'steelblue'.
    - all_colorful (bool, optional): Whether to color all macroscale nodes (True)
        or only those that combine multiple nodes in the microscale network (False).
    - node_cmap (string): a matplotlib cmap. Default is 'Set2'.
    - method_title (string): title of the method to be printed on top of the figure. Default is None.

    Returns:
    - None: This function plots and displays the microscale
            and macroscale networks side by side.
    """
    # Create a figure with two subplots for microscale and macroscale networks
    fig, ax = plt.subplots(1,2,figsize=(10,4.5),dpi=200)
    if method_title is not None:
        fig.suptitle(method_title, fontsize=18, va='bottom')
    
    # get the mapping from pd dataframe to dictionary
    micro2macro_dict = get_micro2macro_dict_from_pd_df(mapping)
    # get the inverse mapping from macronodes to the list of its corresponding micronodes
    macro2microlist_dict = get_macro2microlist_dict_from_micro2macro_dict(micro2macro_dict)
    
    # Position the nodes of the microscale network using a spring layout
    pos_micro = nx.spring_layout(G_micro)
    
    # for positioning the macroscale network, we assign the center of mass of the microscale network
    pos_macro = {}
    for macro_node, micro_nodes in macro2microlist_dict.items():
        pos_macro[macro_node] = np.mean([pos_micro[micro_node] for micro_node in micro_nodes],axis=0)

    # define a different color for each macro_node
    if all_colorful == True:
        macro_colors = mpl.colormaps[node_cmap](np.linspace(0,1,G_macro.number_of_nodes()))
        macro_colors_dict = {}
        for i,macro_node in enumerate(pos_macro.keys()):
            macro_colors_dict[macro_node] = macro_colors[i]
    else:
        number_of_big_macro_nodes = len([_ for _ in macro2microlist_dict.values() if len(_) > 1])
        macro_colors = mpl.colormaps[node_cmap](np.linspace(0,1,number_of_big_macro_nodes))
        macro_colors_dict = {}
        index_color = 0
        for macro_node in pos_macro.keys():
            if len(macro2microlist_dict[macro_node]) > 1:
                macro_colors_dict[macro_node] = macro_colors[index_color]
                index_color += 1
            else:
                macro_colors_dict[macro_node] = nc
        
    # define the color of micro nodes based on the corresponding macro_node
    micro_colors_dict = {}
    for micro_node in pos_micro.keys():
        micro_colors_dict[micro_node] = macro_colors_dict[micro2macro_dict[micro_node]]
    
    # PLOT MICROSCALE NETWORK
    # labels = nx.get_edge_attributes(G_micro,'weight')
    nx.draw(G_micro, pos_micro,
            ax=ax[0],
            node_size=min_ns,
            node_color=[micro_colors_dict[node] for node in G_micro],
            # edge_labels=labels,
            edgecolors=nec
           )
    # get minimum and maximum edge weight
    min_weight_micro = 1000000000
    max_weight_micro = -1000000000
    for edge in G_micro.edges(data='weight'):
        min_weight_micro = min(min_weight_micro, edge[2])
        max_weight_micro = max(max_weight_micro, edge[2])
    # rescale edge_weight
    def rescale_weight(
        weight, 
        min_weight=min_weight_micro, 
        max_weight=max_weight_micro,
        min_size=min_lw, 
        max_size=max_lw,
    ):
        if max_size == min_size:
            return min_size
        else:
            return min_size + (weight - min_weight)/(max_weight - min_weight)*(max_size - min_size)
        
    for edge in G_micro.edges(data='weight'):
        nx.draw_networkx_edges(G_micro,pos_micro,
                               ax=ax[0],
                               edgelist=[edge], 
                               width=rescale_weight(edge[2]),
                               edge_color=ec,
                              )
    
    # PLOT MACROSCALE NETWORK
    # rescale node_weight
    min_weight_macro = 1
    max_weight_macro = max([len(_) for _ in macro2microlist_dict.values()])
    def rescale_weight(
        weight, 
        min_weight=min_weight_macro, 
        max_weight=max_weight_macro,
        min_size=min_ns, 
        max_size=max_ns,
    ):
        if max_size == min_size:
            return min_size
        else:
            return min_size + (weight - min_weight)/(max_weight - min_weight)*(max_size - min_size)
        
    # plot macroscale network
    nx.draw(G_macro, pos_macro,
            ax=ax[1],
            node_size=[rescale_weight(len(macro2microlist_dict[node])) for node in G_macro],
            node_color=[macro_colors_dict[node] for node in G_macro],
            edgecolors=nec
           )
    
    # get minimum and maximum edge weight
    min_weight_macro = 1000000000
    max_weight_macro = -1000000000
    for edge in G_macro.edges(data='weight'):
        min_weight_macro = min(min_weight_macro, edge[2])
        max_weight_macro = max(max_weight_macro, edge[2])
    # rescale edge_weight
    def rescale_weight(
        weight, 
        min_weight=min_weight_macro, 
        max_weight=max_weight_macro,
        min_size=min_lw, 
        max_size=max_lw,
    ):
        if max_size == min_size:
            return min_size
        else:
            return min_size + (weight - min_weight)/(max_weight - min_weight)*(max_size - min_size)
        
    for edge in G_macro.edges(data='weight'):
        nx.draw_networkx_edges(G_macro,pos_macro,
                               ax=ax[1],
                               edgelist=[edge], 
                               width=rescale_weight(edge[2]),
                               edge_color=ec,
                              )

    ax[0].set_title('Original network')
    ax[1].set_title('Coarse-grained network')

    plt.show()