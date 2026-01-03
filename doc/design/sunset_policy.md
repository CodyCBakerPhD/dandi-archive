# Data 'Sunsetting' Policy

## Current Policy

From the **Retention period** section of the [main DANDI docs](https://docs.dandiarchive.org/terms-policies/policies/#longevity) (or [persistent commit link](https://github.com/dandi/dandi-docs/blob/1ee896c9e52f9ae5c5e06bcf978eb024d0de741a/docs/terms-policies/policies.md?plain=1#L70-L92)):

> Versioned items will be retained for the lifetime of the repository. This is currently the lifetime of the NIH award, which currently expires in April 2029.



## Storage Limits

The Open Data program has indicated some hesitancy around massively increasing storage allotment for our S3 bucket.

Estimate around 2.6 PB ceiling before we will need to seriously consider taking some kind of action to reduce our usage.



## The Problem

Current DANDI storage (without garbage collection) is somewhere around 1.2 PB as of early 2026.

There are plans for rapid increases due to upcoming microscopy datasets related to BICAN as well as a potential LINC migration.

Current estimates for these incoming datasets are 1 PB per year for BICAN, for the next 5 years; and one-time 500 TB for LINC.

Within the next two years, we would then expect to start to push the bounds of our storage allotment, and within 5 years we would be well beyond it.



## Proposal: Data 'Sunsetting'

One way of dealing with this would be to treat the S3 bucket as a 'hot cache' of all total contributions to the archive while delegating any unused or least-used contents to some form of cold storage, which could possibly be the chosen backup strategy from the 'Backup (All Options)' document.

The cold storage solution would be distinct from the Open Data program's S3 bucket, and would ideally be a free or low-cost storage solution.

Content in cold storage would:
- **not** be directly accessible to users via DANDI API on-demand.
- be restorable to the main DANDI S3 bucket upon user request, with some expected delay (e.g., hours, days, or weeks).
- be retained for the lifetime of the repository (i.e., after April 2029 until some other date TBD), in accordance with current DANDI policies.



## Analytics from logs

TODO: Analyze access logs to determine how much of bulk content is actually regularly used.



## Specific Recommendation

Based on the above analysis, X% of S3 bucket storage could be offloaded to cold storage without significantly impacting user experience.

I thus propose the following policy change:

> All assets above Y GB in size that have not been fully accessed in the last Z months will be automatically transferred to cold storage.



## Interaction with 'Bulk Data Content' design doc

In application to the current state of the archive, this policy may affect files that contain a mixture of raw and processed data.

The processed portion of such files is often exceptionally small compared to the raw, and is more often used for reanalysis.

Thus, it is possible that certain files that qualify for sunsetting may have small portions that are still regularly accessed.

This problem is easier to solve when combined with the 'Bulk Data Content' design doc proposal, which advocates for separating raw and processed data into distinct files.

Many Dandisets already follow this practice, but it is not outright enforced nor encouraged via validation tools.
