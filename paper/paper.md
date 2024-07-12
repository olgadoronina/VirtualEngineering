---
title: 'Virtual Engineering: A Python package for low-temperature biomass conversion'
tags:
  - Python
  - simulation
  - biofuel

authors:
  - name: Ethan Young
    orcid: 0000-0000-0000-0000
    corresponding: true # (This is how to denote the corresponding author)
    affiliation: 1 # (Multiple affiliations must be quoted)
  - name: Hariswaran Sitaraman
    affiliation: 1
  - name: Olga Doronina
    affiliation: 1
  - name: Andrew Glaws
    affiliation: 1
  - name: Nicholas Carlson
    affiliation: 1
affiliations:
 - name: National Renewable Energy Laboratory, USA
   index: 1
date: 09 November 2023
bibliography: paper.bib

# Optional fields if submitting to a AAS journal too, see this blog post:
# https://blog.joss.theoj.org/2018/12/a-new-collaboration-with-aas-publishing
aas-doi: 10.3847/xxxxx <- update this with the DOI from AAS once you know it.
# aas-journal: Astrophysical Journal <- The name of the AAS journal.
---

# Summary

Virtual Engineering (VE) is a software framework that accelerates research and development and reduces risks for market-relevant biomass conversion processes. VE package supports multi-physics models of unit operations and joins them to simulate the entire end-to-end process of low-temperature conversion of lignocellulosic biomass to a fuel precursor. The framework includes a user-friendly interface that helps engineers seamlessly connect unit operations and enable optimization. We
currently support multiple models, computing paradigms, and fidelities representing the steps of feedstock pretreatment, enzymatic hydrolysis, and bioconversion. Although the VE approach was developed to support a biomass workflow, we have designed each component in a way that allows us to easily support new domains, unit models, and feedstocks.

# Statement of need

Currently, process-modeling TEA does not utilize state-of-the-art mechanistic models

First-of-kind systems-modeling approach for biomass conversion 

# Methods 

Jupyter notebooks and Python programming used to create a graphical user interface (GUI).

The vebio Python package (developed in this project) contains functionality to create and interact with GUI elements and facilitate information transfer between unit operation models.

Sub-models written in different programming languages and have different computing needs: high-fidelity models (CFD simulations) of unit operations are automatically submitted to the NREL HPC scheduler, while lower-fidelity models and surrogates are run directly on the user’s workstation.

# (Mention a representative set of past or ongoing research projects using the software and recent scholarly publications enabled by it)

Automatic TEA analysis of novel bioreactor designs. 
Scale up of bioreactor models. Adaptive computing is a new engagement, generally speaking, projects which need multi-fidelity, multi-scale support to build and connect models for simulations and optimizations.

# Acknowledgements

This work was authored by the National Renewable Energy Laboratory, operated by Alliance for Sustainable Energy, LLC, for the U.S. Department of Energy (DOE) under Contract No. DE-AC36-08GO28308. Funding provided by U.S. Department of Energy Bioenergy Technologies Office (BETO). The views expressed in the article do not necessarily represent the views of the DOE or the U.S. Government. The U.S. Government retains and the publisher, by accepting the article for publication, acknowledges that the U.S. Government retains a nonexclusive, paid-up, irrevocable, worldwide license to publish or reproduce the published form of this work, or allow others to do so, for U.S. Government purposes.

# References