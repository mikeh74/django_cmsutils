from filer.models import Image


def get_image_by_url(url):
    """
    Given a URL, this function retrieves the image object from the database.
    If the image does not exist, it returns None.
    """

    # Start by normalizing the URL to ensure consistency
    normalized_url = url.strip().lower()

    # build the path

    # check if it's a thumbnail eg:
    # /media/filer_public_thumbnails/filer_public/07/56/07566877-e246-4ff6-b877-f4733c988ddf/img4.jpg__40x40_q85_crop_subsampling-2.jpg

    if url.startswith("/media/filer_public_thumbnails/"):
        # Remove the thumbnail prefix and suffix to get the original image URL
        normalized_url = normalized_url.replace(
            "/media/filer_public_thumbnails/", "/media/filer_public/"
        )
        # Remove the thumbnail suffix (e.g., __40x40_q85_crop_subsampling-2.jpg)
        normalized_url = normalized_url.split("__")[0]

    # if it is then rewrite to remove /filer_public_thumbnails and the thumbnail suffix

    try:
        # Attempt to retrieve the image object from the database using the normalized URL
        return Image.objects.get(file__url=normalized_url)
    except Image.DoesNotExist:
        return None
