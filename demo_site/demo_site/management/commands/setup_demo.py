"""
Management command to set up initial demo site data.
"""

from cms.api import create_page
from django.conf import settings
from django.contrib.sites.models import Site
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Create initial demo site data (site and home page)"

    def handle(self, *args, **options):
        # Update the default site
        site = Site.objects.get(pk=settings.SITE_ID)
        if site.domain == "example.com":
            site.domain = "localhost:8000"
            site.name = "Core Plugins Demo"
            site.save()
            self.stdout.write(self.style.SUCCESS(f"✓ Updated site: {site.name} ({site.domain})"))
        else:
            self.stdout.write(self.style.WARNING(f"Site already configured: {site.name} ({site.domain})"))

        # Check if home page already exists
        from cms.models import Page

        if Page.objects.filter(node__depth=1).exists():
            self.stdout.write(self.style.WARNING("Home page already exists, skipping creation"))
            return

        # Create home page
        home_page = create_page(
            title="Home",
            template="base.html",
            language="en",
            slug="",
            in_navigation=True,
        )

        # Update page content with additional metadata
        page_content = home_page.get_content_obj(language="en")
        if page_content:
            page_content.page_title = "Welcome to Core Plugins Demo"
            page_content.menu_title = "Home"
            page_content.meta_description = "Demo site for Django CMS Core Plugins"
            page_content.save()

        self.stdout.write(self.style.SUCCESS(f"✓ Created home page: {home_page.get_title('en')}"))
        self.stdout.write(self.style.SUCCESS("\nDemo site setup complete!"))
        self.stdout.write("  - Visit: http://localhost:8000/")
        self.stdout.write("  - Admin: http://localhost:8000/admin/")
