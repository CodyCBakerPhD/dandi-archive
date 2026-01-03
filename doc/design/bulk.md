# Bulk Data Content

## Definitions

**Bulk (data)**: the largest data arrays within an NWB file.



## Content




## Problem 1: Combined files

It is possible for NWB files to contain both raw and processed data inside the same DANDI asset.

However, in most of the cases when this storage pattern is utilized, the result is that the raw data ends up being much larger than any other data stream in the file, and thus comprises the bulk of the file content.

While this has some measure of convenience in the way of reducing the overall number of assets in a Dandiset, it leads to the following problems:
- Large file sizes that make downloading and uploading cumbersome.
- Difficulties in sharing only the relevant parts of the data with collaborators.
- Challenges in managing and versioning data, as changes to one part of the file may require re-uploading the entire file.

So far, the answer to most of these problems has been to utilize streaming methods to access the file contents rather than outright downloading.

While streaming is a wonderful and amazingly convenient feature, it is perhaps only a bandaid over the underlying inconvenient storage pattern.



## Problem 2: Duplicated Processing and Metadata

Another data storage strategy that has been attempted is to store combined files with both raw and processed data, but to then also store adjacent copies of those files without the raw data present.

While this solves some of the problems mentioned above, it leads to a separate issue; if there any changes made to the metadata or processed data streams, then those changes must also be replicated across both files.

This means the raw data file must also be reuploaded, even possibly republished, even if only a relatively small change was made to the file.



## Perspective: Different Re-Use Cases

Different re-users have different needs when it comes to accessing and data stored in NWB files on DANDI.

Here are some common scenarios:
1. **Raw Data Re-Use**: A researcher wants to access only the raw data for re-analysis or to apply new processing techniques. They may not need the processed data at all.
2. **Processed Data Re-Use**: A user is interested in only the processed data for their analysis, without needing to download the raw data.
3. **Full Data Re-Use**: In some cases, a user may need access to both raw and processed data for comprehensive analysis, such as reproduction of all original findings.



## Perspective: Using DANDI as a Live Service

It is also possible for users to leverage the DANDI archive as a storage service for live processing.

In this usage model, experimenters actively upload all of their raw data directly after acquiring it, and perform data processing and analysis in real time.

Data is transferred from the S3 bucket to whatever the source of primary compute is, which can possibly include in-region EC2 such as the DANDI Hub.

Most users following this pattern leverage the embargo feature, and do not finalize their data content until it is time to unembargo.

With this model, the bulk data begins as distinct files and is only later combined into NWB files for final publication at the behest of the experimenter, though because this step requires a fair amount of additional processing it is not often done.



## Analytics

A basic analysis of how bulk content is distributed across DANDI is seen through the following script:

<details>

```python
# TODO
```

</details>



## Case Studies

It may help to precisely clarify the issues above with some existing Dandisets.

### ??

### ??



## Recommendation

I recommended adding and enforcing (via validation) the policy that users should strictly separate bulk data content from other data streams within NWB files whenever possible.

By 'strict' I mean without any duplication of file content aside from metadata requirements, which should be minimized in the file containing bulk. An example of such minimization would be the removal of insertion locations/coordinates from the raw file since those can often be adjusted post-hoc in the lighter weight processed files.

This would likely include adding utility functions, documentations, and/or guidelines to help users restructure their data storage patterns.



## Interaction with 'Data Sunsetting' design doc

If a data sunsetting policy is adopted, I would also recommend suggesting to past data submitters of particularly large Dandisets to re-publish their data with bulk content separated out.

The previously published versions would then 'sunset' after an appropriate amount of time, freeing up the storage duplicated from republication.



## Interaction with 'Virtual Datasets' design doc

TODO: highlight interactions with virtualized datasets
