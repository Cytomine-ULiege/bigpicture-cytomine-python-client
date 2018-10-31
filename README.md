# Cytomine Python client

> Cytomine-python-client is an open-source Cytomine client written in Python. This client is a Python wrapper around Cytomine REST API gateway.

[![Build Status](https://travis-ci.com/Cytomine-ULiege/Cytomine-python-client.svg?branch=master)](https://travis-ci.com/Cytomine-ULiege/Cytomine-python-client)
[![GitHub release](https://img.shields.io/github/release/Cytomine-ULiege/Cytomine-python-client.svg)](https://github.com/Cytomine-ULiege/Cytomine-python-client/releases)
[![GitHub](https://img.shields.io/github/license/Cytomine-ULiege/Cytomine-python-client.svg)](https://github.com/Cytomine-ULiege/Cytomine-python-client/blob/master/LICENSE)

## Overview

The main access point to Cytomine data is its REST API. This client is a Python package that can be imported in an application and allows to import/export data from Cytomine-Core and Cytomine-IMS using RESTful web services e.g. to generate annotation (spatial) statistics, create regions of interest (e.g. tumor masks), add metadata to images/annotations, apply algorithms on image tiles, ...

See [documentation](http://doc.cytomine.be/display/ALGODOC/%5BDOC%5D+Data+access) for more details.

## Requirements
* Python 2.7 | 3.5+

## Install

**To install *official* release of Cytomine-python-client, see @cytomine. Follow this guide to install forked version by ULiege.** 

### Manual installation
To download and install manually the package, see [manual installation procedure](http://doc.cytomine.be/display/ALGODOC/How+to+install+the+Cytomine+Python+Client).

### Automatic installation
To retrieve package using Maven or Gradle, see [package repository](https://packagecloud.io/cytomine-uliege/Cytomine-python-client).


## Usage

See [detailed usage documentation](http://doc.cytomine.be/display/DEVDOC/Part+5%3A+Cytomine+Python+Client).

### Basic example
Three parameters are required to connect:
* `CYTOMINE_URL`: The full URL of Cytomine core (e.g. “http://demo.cytomine.be”).
* `PUBLIC_KEY`: Your cytomine public key.
* `PRIVATE_KEY`: Your cytomine private key. 

First, the connection object has to be initialized.   
    
    TODO

The next sample code should print “Hello {username}” where {username} is replaced by your Cytomine username and print the list of available projects.

    TODO

## References
When using our software, we kindly ask you to cite our website url and related publications in all your work (publications, studies, oral presentations,...). In particular, we recommend to cite (Marée et al., Bioinformatics 2016) paper, and to use our logo when appropriate. See our license files for additional details.

- URL: http://www.cytomine.org/
- Logo: [Available here](https://cytomine.coop/sites/cytomine.coop/files/inline-images/logo-300-org.png)
- Scientific paper: Raphaël Marée, Loïc Rollus, Benjamin Stévens, Renaud Hoyoux, Gilles Louppe, Rémy Vandaele, Jean-Michel Begon, Philipp Kainz, Pierre Geurts and Louis Wehenkel. Collaborative analysis of multi-gigapixel imaging data using Cytomine, Bioinformatics, DOI: [10.1093/bioinformatics/btw013](http://dx.doi.org/10.1093/bioinformatics/btw013), 2016. 

## License

Apache 2.0



----

See examples in https://github.com/cytomine/Cytomine-python-client/tree/master/client/examples and https://github.com/cytomine/Cytomine-python-client/tree/master/utilities/examples

The client is automatically installed with the Docker/Bootstrap procedure, however it is possible to install it independently
on remote computers. See installation instructions here:
http://doc.cytomine.be/pages/viewpage.action?pageId=12321357
