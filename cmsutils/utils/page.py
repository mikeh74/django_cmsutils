# from cms.api import add_plugin
from cms.models import PageContent
from djangocms_versioning.constants import DRAFT
from djangocms_versioning.models import Version


def page_has_draft(page, language):
    """
    Check if a draft exists for the given page and language.
    """
    return PageContent.admin_manager.filter(
        page=page,
        language=language,
        versions__state=DRAFT,
    ).exists()


def get_or_create_draft(page, language, created_by=None):
    """
    Get the draft for the given page and language, or create one if it doesn't exist.
    """
    draft = PageContent.admin_manager.filter(
        page=page,
        language=language,
        versions__state=DRAFT,
    ).first()

    if draft:
        return draft

    # No draft exists → create one from the published version
    published = PageContent.objects.get(page=page, language=language)
    published_version = published.versions.first()
    
    if published_version:
        # Copy the published version to create a draft
        # The copy() method requires a created_by parameter
        draft_version = published_version.copy(created_by=created_by)
        return draft_version.content
    else:
        # Fallback: create a version directly if none exists
        version = Version.objects.create(content=published, created_by=created_by)
        return version.content


def update_draft_content(draft, title, description):
    """
    Update the draft content with the given title and description.
    """

    if title is not None:
        draft.page_title = title

    if description is not None:
        draft.page_description = description

    draft.save()


def publish_draft(draft_content, user=None):
    """
    Publish the given draft content.
    """
    version = draft_content.versions.first()
    if version:
        version.publish(user=user)


def update_page(page, language="en", data=None, user=None):
    """
    Update the given page with the provided data.

    This function will:
    1. Get or create a draft for the page in the specified language.
    2. Update the draft's content with the provided title and description.
    3. Publish the draft to make the changes live.

    """

    # Step 1: get or create draft
    draft = get_or_create_draft(page, language, created_by=user)

    data = data or {}
    title = data.get("title")
    description = data.get("description")

    # Step 2: update draft placeholders
    update_draft_content(
        draft,
        title=title,
        description=description,
    )

    # Step 3: publish
    publish_draft(draft, user=user)
