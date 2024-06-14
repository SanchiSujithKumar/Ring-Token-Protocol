# Ring Token Protocol Implementation and Optimization

This project implements and optimizes the Ring Token Protocol for efficient message passing in a network of nodes. The implementation consists of two primary directories: `base` and `node`, each containing different versions of the protocol. This README provides an overview of the project, setup instructions, and usage guidelines.

## Table of Contents

- [Introduction](#introduction)
- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
  - [Base Station](#base-station)
  - [Node](#node)
- [Configuration](#configuration)
- [Contributing](#contributing)
- [Authors](#authors)

## Introduction

The Ring Token Protocol is a network communication protocol where nodes are arranged in a logical ring. A token circulates around the ring, granting the node holding it permission to send messages. This project implements the protocol with added features for optimization, such as packet distribution and retransmission handling.

## Features

- Token-based message passing
- Efficient packet distribution among nodes
- Retransmission handling for reliable delivery
- Time tracking and token holding time management
- Dynamic ring expansion
- Graceful exit for nodes (in specific versions)

## Requirements

- Python 3.x
- Standard Python libraries (`socket`, `threading`, `json`, `random`, `bisect`, `collections`)

## Installation

1. Clone the repository to your local machine:

```bash
git clone https://github.com/SanchiSujithKumar/Ring-Token-Protocol.git
cd Ring-Token-Protocol
```

2. Ensure you have Python 3.x installed on your machine.

## Usage

### Base Station

Navigate to the `base` directory and run one of the base station scripts:

```bash
cd base
python base_station_standard.py
```

Alternatively, you can run the optimized or exit-enabled versions:

```bash
python base_station_optimized.py
# or
python base_station_with_exit.py
```

- **base_station_optimized.py**: Optimized version of the base station.
- **base_station_standard.py**: Standard version of the base station.
- **base_station_with_exit.py**: Version of the base station with exit functionality.

### Node

Navigate to the `node` directory and run one of the node scripts in separate terminal windows:

```bash
cd node
python node_standard.py
```

Alternatively, you can run the optimized or exit-enabled versions:

```bash
python node_optimized.py
# or
python node_with_exit.py
```

- **node_optimized.py**: Optimized version of the node.
- **node_standard.py**: Standard version of the node.
- **node_with_exit.py**: Version of the node with exit functionality.

### Example Interaction

1. Start the base station:

```bash
python base/base_station_standard.py
```

2. Start multiple nodes in separate terminal windows:

```bash
python node/node_standard.py
```

3. Follow the prompts in each node window to send messages and interact with the network.

## Configuration

- **Token Timeout:** Configurable in the `set_tl` and `reset_tl` functions within the node scripts.
- **Maximum Number of Packets:** Configurable via the `MAX_NOP` variable in the node scripts.

## Contributing

This is a group project developed by three contributors. Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.

## Authors

This project was built by Sujith Kumar Sanchi, Sree Naga Manikanta Katta, and Revanth Palaparthi.