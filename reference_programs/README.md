# Reference Programs

This folder stores two open-source projects that are highly relevant to this bike-sharing rebalancing project. They are kept as reference programs for future code organization, modeling ideas, and implementation details.

## `citibike_rebalancing`

Source repository: `melaniezheng/citibike_rebalancing`

Why it is similar:

- It also works on CitiBike rebalancing.
- It predicts outgoing demand, incoming demand, and station depletion status by date/time.
- It generates pairing suggestions about which stations should send bikes to which other stations.

What can be borrowed directly:

- CitiBike data cleaning and feature engineering.
- Random Forest based demand prediction.
- Station status/depletion prediction.
- The workflow from demand prediction to rebalancing suggestions.

## `bss-inventory-rebalancing`

Source repository: `joeycyhuang/bss-inventory-rebalancing`

Why it is similar:

- It directly implements bike-sharing inventory rebalancing.
- It converts mathematical methods from bike-sharing inventory rebalancing and vehicle routing literature into Python code.
- It applies the idea to Taipei YouBike.

What can be borrowed directly:

- Module organization around routing, clustering, and service level.
- `routing.py` for vehicle routing implementation ideas.
- `service_level.py` for service-level/inventory evaluation ideas.
- The way inventory rebalancing is connected with routing decisions.

These projects are included for reference and comparison. Before copying code into the main implementation, check each project's license and keep attribution.
