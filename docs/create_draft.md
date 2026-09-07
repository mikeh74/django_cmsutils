# Creating draft page in Django CMS

### **Concise takeaway**  

In **django CMS 5 + djangocms‑versioning**, you **never update a page directly**.
You **must** update its **draft `PageContent`**, and if no draft exists, you **create a new Version**, modify its placeholders, then **publish** when ready.

Below is the correct, production‑safe workflow.

---

# ✅ **The correct programmatic workflow**

There are **three distinct steps**:

---

## **1. Get (or create) the draft version**
A page can have **multiple languages**, so you always work at the `PageContent` level.

```python
from cms.models import PageContent
from djangocms_versioning.constants import DRAFT
from djangocms_versioning.models import Version

def get_or_create_draft(page, language):
    # Try to fetch an existing draft
    draft = PageContent.admin_manager.filter(
        page=page,
        language=language,
        versions__state=DRAFT,
    ).first()

    if draft:
        return draft

    # No draft exists → create one from the published version
    published = PageContent.objects.get(page=page, language=language)
    return Version.objects.create(content=published).copy()
```

This gives you a **draft PageContent** that you can safely modify.

---

## **2. Modify the draft’s placeholders**
Every page has placeholders; you edit their plugins inside the draft version.

```python
from cms.api import add_plugin

def update_draft_content(draft_content):
    placeholder = draft_content.get_placeholder("content")

    # Remove existing plugins if needed
    placeholder.cmsplugin_set.all().delete()

    # Add new plugin content
    add_plugin(
        placeholder=placeholder,
        plugin_type="TextPlugin",
        language=draft_content.language,
        body="Updated content from script",
    )
```

This updates the draft version only — **public content remains untouched**.

---

## **3. Publish the draft**
Publishing is done through the versioning API:

```python
def publish_draft(draft_content):
    version = draft_content.versions.first()
    version.publish()
```

This replaces the public version with the draft.

---

# 🧩 **Full working example (end‑to‑end)**

```python
def update_page(page, language="en"):
    # Step 1: get or create draft
    draft = get_or_create_draft(page, language)

    # Step 2: update draft placeholders
    update_draft_content(draft)

    # Step 3: publish
    publish_draft(draft)
```

This is the **canonical** way to programmatically update a page in django CMS 5 with versioning.

---

# 🧠 **Non‑obvious insight**
When you call:

```python
Version.objects.create(content=published).copy()
```

Versioning **duplicates the PageContent and all its plugins**, creating a proper draft.  
If you skip this and modify the published version directly, you will **silently bypass versioning**, and your edits will go live immediately.

This is the #1 mistake developers make when scripting updates.

