from django.contrib import admin

from .models import Event


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Event._meta.fields]
    list_filter = [
        "status",
        "created",
    ]
    search_fields = ["title", "description"]
    raw_id_fields = ["owner"]
    date_hierarchy = "date"
    ordering = ["-date", "-time"]
    show_facets = admin.ShowFacets.ALWAYS
