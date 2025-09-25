import os
import re
import ipaddress
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.offsetbox import OffsetImage, AnnotationBbox

CONFIG_DIR = r"G:\config"
G = nx.Graph()
edge_labels = {}

# Paths to your custom images (ensure these images are in the same directory)
router_img_path = "router.jpeg"  # The images themselves are JPEG
switch_img_path = "switch.jpeg"  # The images themselves are JPEG

# Read all dump files
for filename in os.listdir(CONFIG_DIR):
    if filename.endswith(".dump"):
        device = filename.replace(".dump", "")
        with open(os.path.join(CONFIG_DIR, filename)) as f:
            content = f.read()
            
            # Get all interface blocks
            interfaces = re.findall(r"interface\s+\S+([\s\S]*?)(?=!\n|$)", content)
            for block in interfaces:
                # Only consider interfaces with description (links)
                desc_match = re.search(r"description\s+link to (\w+)", block, re.IGNORECASE)
                if not desc_match:
                    continue
                neighbor = desc_match.group(1)
                G.add_edge(device, neighbor)

                # IP address and network
                ip_match = re.search(r"ip address\s+(\d+\.\d+\.\d+\.\d+)\s+(\d+\.\d+\.\d+\.\d+)", block)
                if ip_match:
                    ip = ip_match.group(1)
                    mask = ip_match.group(2)
                    # Calculate network
                    network = ipaddress.IPv4Network(f"{ip}/{mask}", strict=False)
                    network_label = str(network)
                else:
                    network_label = ""

                # Bandwidth
                bw_match = re.search(r"bandwidth\s+(\d+)", block)
                if bw_match:
                    bw = int(bw_match.group(1))
                else:
                    bw = 0

                # Edge label: network + bandwidth
                label = f"{network_label}\n{bw} Mbps"
                edge_labels[(device, neighbor)] = label

# Draw topology
pos = nx.spring_layout(G, seed=42)

# Draw edges
nx.draw_networkx_edges(G, pos, width=2)
nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=8)

# Draw custom images for nodes
ax = plt.gca()
ax.set_axis_off()
for node in G.nodes():
    x, y = pos[node]
    
    # Logic to determine if a node is a 'router' or 'switch'
    if node.startswith("R"):
        img = plt.imread(router_img_path)
    elif node.startswith("SW"):
        img = plt.imread(switch_img_path)
    else:
        # Fallback to a default image if the naming convention isn't followed
        img = plt.imread(router_img_path)
        
    imagebox = OffsetImage(img, zoom=0.1) # Adjust zoom as needed
    ab = AnnotationBbox(imagebox, (x, y), frameon=False, pad=0.0)
    ax.add_artist(ab)
    
    # Draw node labels slightly below the image
    plt.text(x, y - 0.1, node, ha='center', va='top', fontsize=10, weight='bold')

plt.title("Auto-Generated Network Topology")
plt.axis("off")
plt.savefig("topology.png") # Changed the file extension back to .png
plt.show()