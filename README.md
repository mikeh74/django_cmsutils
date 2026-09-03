# CMS Utils

This package is intended to support custom functionality required internally.

Primarily we are targeting automation and management tasks to help support the
marketing team with SEO tasks that are increasingly taking up a lot of time.

## Quick start

1. Add "cmsutils" to your INSTALLED_APPS setting like this:

  ```
      INSTALLED_APPS = [
          ...
          'cmsutils',
      ]
  ```

2. Run ``python manage.py migrate`` to create the models.

3. Start the development server and visit <http://127.0.0.1:8000/>
   and go to the admin panel and select CMS Utilities.

## Functionality

* [Image updates](./docs/image_updates.md)
* [Page updates](./docs/page_updates.md)
