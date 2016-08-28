# Brainstorm Network

Brainstorm network is an application to organize ideas as a network. Each concept is a node of the network and the edges represent the relationship between two nodes. This relationship can have a qualifier like a weight or other information like 'increase', 'decrease', 'rare' etc.

In this application the user has complete control to create types of
  - Nodes
  - Edges
  - Qualifiers

You can also:
  - Import references from a bibtex file.
  - Associate information to an edge, making reference to an entry of your bibfile.

This project is a personal effort to organize my own ideas.
It is in the beginning, accepting collaboration.

### Version
0.0.1

### Tech

The main requirement is the web2py application:
* [Web2Py](https://github.com/web2py/web2py/) - Free and open source full-stack enterprise framework for agile development of secure database-driven web-based applications, written and programmable in Python.

### Installation

The steps to run this application are:
- You need to download the web2py from their git repository:
- Inside of the web2py *applications* folder clone this project.
- Copy *private/appconfig.ini* from the web2py *welcome* application into the Brainstorm application folder *private*. After this, configure this file with your preferences of database.
- run the web2py server.

### Screenshot

Brainstorm Network Visualization
![alt text][network]


[network]: https://github.com/axnsantana/brainstorm-network/blob/master/screenshots/network.png
