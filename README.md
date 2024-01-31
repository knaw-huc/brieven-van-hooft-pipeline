# Brieven van Hooft pipeline

*(this is a very preliminary text missing details)*

## Introduction

The aim of this project is to make the *Brieven van [P.C.
Hooft](https://nl.wikipedia.org/wiki/Pieter_Corneliszoon_Hooft)* better 
accessible to researchers. 

These have been linguistically enriched in an earlier project *(which? how?)* and
delivered in [FoLiA XML](https://proycon.github.io/folia) format. We intend to
produce W3C Web Annotations via [STAM](https://annotation.github.io), so the
texts and any annotations can ultimately be showed and queried via
[TextAnnoViz](https://github.com/knaw-huc/textannoviz), a web-application that
builds upon other infrastructure
([TextRepo](https://github.com/knaw-huc/textrepo),
[AnnoRepo](https://github.com/knaw-huc/annorepo),
[Broccoli](https://github.com/knaw-huc/broccoli)) at KNAW HuC's Team Text.

This project serves a test-case to use STAM as a pivot model for untangling
FoLiA and making it available as W3C Web Annotations.

## Data

*(Describe the current state of the data and its licensing)*

## Use case

*(Describe the wishes and requirements from the researcher's perspective)*

## Requirements

* **Software:** `folia2stam` - FoLiA XML to STAM converter, already largely implemented in [folia-tools](https://github.com/proycon/folia-tools).
* **Software:** [STAM-tools](https://github.com/annotation/stam-tools) - Tooling for dealing with STAM
* **Software:** [TextRepo](https://github.com/knaw-huc/textrepo) - Backend repository to store and index corpora with metadata and versions
* **Software:** [AnnoRepo](https://github.com/knaw-huc/annorepo) - A webservice for W3C Web Annotations, implementing the W3C Web Annotation Protocol.
* **Software:** [Broccoli](https://github.com/knaw-huc/broccoli) - Intermediary between various backend storage engines (currently: textrepo, annorepo) and frontend TextAnnoViz.
* **Software:** [TextAnnoViz](https://github.com/knaw-huc/textannoviz) - Frontend to view texts, scans, and annotations.

Some of the above may need some extension and tweaking in the scope of this project.

## Deliverables

* **Software:** A conversion pipeline to take the current form of Brieven van Hooft (FoLiA XML?) and transform it*
 in such a way that it can be shown in TextAnnoViz. This git repository will primarily hold this implementation, its input and output.
    * **Software:** `stam2webanno` - STAM to W3C Web Annotation export. This STAM extension is already [formulated here](https://github.com/annotation/stam/tree/master/extensions/stam-webannotations) but is not implemented yet.
        * *Time estimate:* 40 hours
* **Service:** TextAnnoViz service for Brieven van Hooft
* **Data:** STAM model for Brieven van Hooft. This can be queried and visualised using low-level tools.
* **Data (optional):** Some static HTML visualisations provided via the STAM tooling, not reliant on any further infrastructure.


