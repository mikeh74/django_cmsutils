# Image Updates

In the first instance the scope of the image updates functionality will only
cover updates to alt text for image records.

The process should look something like this:

* Import a spreadsheet (CSV or Excel)
* Populate a table with this data
* Allow admin users to review the imported data
* Allow admin users to select records to update
* Run bulk updates
* Iterate over each selected record:
    * [Parse URL](#parsing-urls)
    * [Normalize URL](#normalizing-urls)
    * Attempt to match image based on normalized URL
    * If we have an image then update the image_alt_text and save
    * update the image upate record to include the date and current user
    * save record
* Report back successes and failures

## Parsing URLs

We are not parsing the URLs at import time to reduce admin user friction
having to clean data and then try to upload again and again but this does mean
that we might have more failures when we try and find image objects.

We use the urllib.parse.urlparse function to parse the raw URLs imported from
the spreadsheet. Parsing the URL does not validate the URL it is
a robust way to extract the *path* from the URL:

```python

>>> from urllib.parse import urlparse

>>> url_str = "http://localhost:8000/media/filer_public_thumbnails/filer_public/07/56/07566877-e246-4ff6-b877-f4733c988ddf/img4.jpg__40x40_q85_crop_subsampling-2.jpg?q=1"

>>> o = urlparse(url_str)
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


