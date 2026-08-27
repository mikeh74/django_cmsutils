from django.contrib.admin.views.main import ChangeList
from django.template.response import TemplateResponse


def approved_list_view(self, request):
    # Base queryset
    qs = self.get_queryset(request).filter(approved_at__isnull=False)

    # Build a ChangeList instance
    cl = ChangeList(
        request,
        self.model,
        self.list_display,
        self.list_display_links,
        self.list_filter,
        self.date_hierarchy,
        self.search_fields,
        self.list_select_related,
        self.list_per_page,
        self.list_max_show_all,
        self.list_editable,
        self,
        sortable_by=self.sortable_by,
        search_help_text=self.search_help_text,
    )

    # Override the queryset
    cl.queryset = qs

    context = {
        **self.admin_site.each_context(request),
        "cl": cl,
        "opts": self.model._meta,
        "title": "Approved Image Updates",
    }

    return TemplateResponse(
        request,
        "admin/change_list.html",
        context,
    )
