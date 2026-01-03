# DANDI Quality Control (QC)

Inspired by [MRIQC](https://mriqc.readthedocs.io/en/latest/).



## The Problem

The DANDI Archive now hosts hundreds of datasets, each containing multiple data streams across imaging, electrophysiology, and behavioral modalities with a significant amount of associated metadata.

Searching for the right dataset for a particular analysis can be challenging, and users often need to sift through large amounts of high-level metadata just to find candidate datasets that then require further investigation before determination of suitability.

While the DANDI team is undertaking efforts to enhance search & findability based on this attached metadata, there is a separate set of measures that many re-users would be interesting in filtering by: quality metrics.

If users had immediate access to such metrics through the high-level metadata, they may not need to comb through the data content to determine if it meets their needs.



## Proposal

I propose the development of a software package devoted to calculating such quality metrics for each asset within a Dandiset and integrating these results into the DANDI metadata.

This system would, wherever possible, leverage existing QC tools from external frameworks.

Finally, nice renderings of such QC results could be integrated into the landing pages of each Dandiset for easy browsing by users.

**I DO NOT PROPOSE** to integrate such QC results with the validation process to exclude datasets that do not meet certain quality thresholds. The goal is simply to provide additional information to users to help them make informed decisions about dataset selection.



## Explicit examples

SpikeInterface has a large number of built-in quality metrics for extracellular electrophysiology data. In fact, the AIND spike sorting pipeline already calculates all of these metrics for each sorting result and stores them within the respective output NWB files.

Some examples of such metrics include:
- TODO: with equations, verbal summary, possible cross-references



## Drawback: The Fear of Judgement

Some data submitters may feel uncomfortable with the idea of having their datasets judged based on such quality metrics.

It could lead to concerns about the potential for negative perceptions of their work, especially if the QC results are made publicly visible.

This is especially so in cases where the QC values are largely outside the control of the experimenters (e.g., older datasets, data collected on older hardware, or data obtained from challenging environments), there may be apprehension about being unfairly judged.
