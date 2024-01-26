from django.urls import path
from .views import (
    index,
    profile,
    edit_profile,
    documents,
    document_detail,
    logout_view,
    text_editor,
    generate_text,
    extend_text_view,
    stye_view,
)

urlpatterns = [
    path("", index, name="dashboard"),
    path("profile/", profile, name="profile"),
    path("profile/edit/", edit_profile, name="edit_profile"),
    path("documents/", documents, name="documents"),
    path("documents/<str:document_id>/", document_detail, name="document_detail_api"),
    path("logout/", logout_view, name="logout"),
    path("generate_content/", text_editor, name="editor"),
    path("generate_text/", generate_text, name="generate_text"),
    path("extend_text_view/", extend_text_view, name="extend_text"),
    path("style/add/", stye_view, name="add_style"),
]
