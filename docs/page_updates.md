# Page Updates

In the first instance the scope of the page updates functionality will only
cover updates to title and description fields.

The requirement is to allow users to upload a spreadsheet which includes URLs
identifying the page that requires updating and the title and description fields
to update.

There are a number of steps required to


The process should look something like this:

* Import a spreadsheet (CSV or Excel)
* Limit import filetypes to .csv .xls .xlsx
* Populate a table with this data
* Allow admin users to review the imported data
* Allow admin users to select records to update
* Run bulk updates
* Iterate over each selected record:
    * [Parse URL](#parsing-urls)
    * [Normalize URL](#normalizing-urls)
    * Attempt to match URL to CMS page or app hook
        * [Page object update](#updating-page-object)
        * [App hook update](#updating-apphook-object)
* Report back successes and failures

Could have audit for previous text.

## Parsing URLs

We are not parsing the URLs at import time to reduce admin user friction
having to clean data and then try to upload again and again but this does mean
that we might have more failures when we try and find image objects.

We use the urllib.parse.urlsplit function to parse the raw URLs imported from
the spreadsheet. Parsing the URL does not validate the URL it is
a robust way to extract the *path* from the URL:

```python

>>> from urllib.parse import urlsplit

>>> url_str = "http://localhost:8000/media/filer_public_thumbnails/filer_public/07/56/07566877-e246-4ff6-b877-f4733c988ddf/img4.jpg__40x40_q85_crop_subsampling-2.jpg?q=1"

>>> o = urlsplit(url_str)
>>> o.path
'/media/filer_public_thumbnails/filer_public/07/56/07566877-e246-4ff6-b877-f4733c988ddf/img4.jpg__40x40_q85_crop_subsampling-2.jpg'
```

## Normalizing URLs

Once we have parsed the URL and extracted the path we still need reduce it down
to a standard string which excludes the `/media` prefix and then checks whether
we the URL is requesting a thumbnailed version of the image.

If it is requesting a thumbnail then we strip those parts of the path to leave
the original file path which we can use to filter for the image object:

```python
    try:
        img = Image.objects.filter(file=obj.normalized_image_url).first()
    except Image.DoesNotExist:
        img = None
```

This returns the first matching record, but since in should be unique this
should be a safe pattern to use.

## Updating records

Depending on whether we are updating a CMS page or an apphook object will change
the workflow involved.

## Updating Page Object

If we are updating a CSM page object then the process is as follows:

* Get the page object
* Check the current status of the page
    * Page is unpblished - do nothing (creating a draft could potentially cause confusion about the state of the page)
    * Page is published - check to see if there is a draft
    * If the page has a draft then do nothing
    * Page is published and has no draft:
        * Create a draft
        * Apply updates to draft
        * Publish draft

If we run into a fail then we collect the information and stored it to use as
feedback for the user.

## Updating Apphook Object

If we are updating any other kind of object then we follow this process:

* Get the object
* Check to see whether we have field mappings to map to title and description for this model
* Build the update statement based on the field mappings
* Upate the record
* Save
* Collect and report failures
