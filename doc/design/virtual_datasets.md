# Virtual Datasets

Virtual datasets are a relatively recent concept for the HDF5/Zarr formats.


## The Problem

Similar to the Bulk Data Content design doc,

However, as I will show in this proposal, the virtual dataset concept can actually help solve many of the problems currently experienced by the archive.


## The Concept



## Benefit 1: Easier file editing



## Benefit 2: Simpler annotations

This would also make it much easier for users external to a Dandiset (e.g., not the original submitters) to suggest/contribute in-place annotations. Of course, anyone can create their own copies of the virtualized content of a Dandiset and annotate those external to the source.



## Benefit 3: Even more flexible deduplication

Perhaps the greatest benefit to the internal infrastructure of the archive would be true deduplication of file content.

The current blob storage system is already quite good at deduplication assets as files based on their checksums, but as shown below in section ?? it is not uncommon to find repeated internal data content scatterd across multiple files.

By pairing the blob storage with virtualized data content, we could deduplicate data content at a much finer granularity.



## Benefit 4: Greater streaming performance

As shown in the NWB Benchmarks paper, LINDI (the virtualized data access layer for NWB files) can provide significant performance improvements for streaming data access.



## Drawback: More complex file content access

Perhaps the greatest drawback to virtual datasets is that they are not intuitive to basic users or heavily integrated into other tools.

A user cannot simply download a file and immediately understand how to access all content.

Basic HDF5/Zarr file viewers (such as HDFView, Neurosift, or Neuroglancer) will not understand the virtualized content without custom reference resolvers which must be externally provided.

We can of course develop our own set of tools and methods for accessing virtualized content, but this reduces accessibility from what it is today.



## Analytics

The following Python script demonstrates the issue of repeated data content spread across disparate files across the archive:

<details>

```python
```

</details>



### Recommendation

I recommend that we begin a phase of experimental adoption by our power users to test out the virtual dataset concept within the archive and then test reception through a series of user tests.

