from django.contrib import admin
from .models import Post, Category, Tag


# Register your models here.
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'status', 'creat_time')
    fields = ('name', 'status', 'website')
    search_fields = ['name']
    list_filter = ('website', )

    def post_count(self, obj):
        return obj.article_set.count

    post_count.short_description = 'post count'


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'status', 'creat_time')
    fields = ('name', 'status', 'website')
    search_fields = ['name']
    list_filter = ('website', )


class CategoryOwnerFilter(admin.SimpleListFilter):
    title = 'Category Filter'
    parameter_name = 'website_category'

    def lookups(self, request, model_admin):
        return Category.objects.filter(website=request.user).values_list('id', 'name')

    def queryset(self, request, queryset):
        category_id = self.value()
        if category_id:
            return queryset.filter(category_id=self.value())

        return queryset


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'website', 'category', 'status', 'creat_time']  # 显示列表的表头
    list_display_links = []  # 显示为链接，可跳转至修改页面
    list_filter = ('website', )

    # list_filter = [CategoryOwnerFilter, ]  # 显示过滤器
    search_fields = ['title', 'website__title', 'category__name']  # 查找字段
    autocomplete_fields = ['category', 'tags']

    fieldsets = (
        ('Title', {
            'description': 'post basic information',
            'fields': ('title', 'status')
        }),
        ('Content', {
            'description': 'add post content',
            'fields': ('website', 'content')
        }),
        ('Category and Tag', {
            'description': 'set the category and tags for post',
            'fields': (('category', 'tags'),
                       )
        })
    )

    filter_horizontal = ('tags', )
