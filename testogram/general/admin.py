from django.contrib import admin
from general.models import User, Reaction, Comment, Post
from django.contrib.auth.models import Group
from rangefilter.filters import DateRangeFilter
from general.filters import AuthorFilter, PostFilter
from django_admin_listfilter_dropdown.filters import ChoiceDropdownFilter



admin.site.unregister(Group)
# admin.site.register(User)

@admin.register(User)
class UserModelAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "first_name",
        "last_name",
        "username",
        "email",
        "is_staff",
        "is_superuser",
        "is_active",
        "date_joined",
    )

    readonly_fields = ("date_joined","last_login",)
    fieldsets = (( "Личные данные", {"fields": ("first_name","last_name","email",)}),
                ("Учетные данные", {"fields": ("username","password",)}),
                ("Статусы", {"classes": ("collapse",),"fields": ("is_staff","is_superuser","is_active",)}),
                (None, {"fields": ("friends",)}),
                ("Даты", { "fields": ( "date_joined","last_login", )})
            )
    
    search_fields = ("id","username","email",)
    list_filter = (
        "is_staff",
        "is_superuser",
        "is_active",
        ("date_joined", DateRangeFilter),
    )

@admin.register(Reaction)
class ReactionModelAdmin(admin.ModelAdmin):
    list_display = ("id","author","post","value",)
    list_display_links = ("id","author",)
    list_filter = (
        PostFilter,
        AuthorFilter,
        ("value", ChoiceDropdownFilter),
    )



@admin.register(Comment)
class CommentModelAdmin(admin.ModelAdmin):
    list_display = ("id","author","post","body","created_at",)
    list_display_links = ("id","body",)
    search_fields = ("author","post",)
    list_filter = (AuthorFilter, PostFilter, "author","post",)

@admin.register(Post)
class PostModelAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "author",
        "title",
        "get_body",
        "created_at",
        "get_comment_count"
    )
    list_display_links = ("id","get_body",)

    fields = ("author","title","body","get_comment_count","created_at",)
    readonly_fields = ("id","created_at","get_body","get_comment_count")
    
    def get_body(self,obj):
        if len(obj.body) > 64:
            return obj.body[:61] + '...'
        return obj.body
    
    def get_comment_count(self,obj):
        return obj.comments.count()
    
    # search_fields = ["author"]
    list_filter = (
        AuthorFilter,
        ("created_at", DateRangeFilter),
        "author",
    )
    
    get_body.short_description = 'body'
    get_comment_count.short_description = 'comment_count'

    
  


# Register your models here.
