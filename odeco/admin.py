from django.contrib import admin


class ViewAdmin(admin.ModelAdmin):
    """
    Custom made change_form template just for viewing purposes
    You need to copy this from /django/contrib/admin/templates/admin/change_form.html
    And then put that in your template folder that is specified in the
    settings.TEMPLATE_DIR
    """
    change_form_template = 'admin/view_form.html'
    change_list_template = 'admin/view_list.html'

    # Remove the delete Admin Action for this Model
    actions = None

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def save_model(self, request, obj, form, change):
        # Return nothing to make sure user can't update any data
        pass
