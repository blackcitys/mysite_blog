from django.shortcuts import render, get_object_or_404
from .models import Blog, BlogType
from django.core.paginator import Paginator
from django.conf import settings
from django.db.models import Count
from read_statistics.utils import read_statistics_once_read


def get_blog_list_common_date(request, blogs_all_list):
    #   获取博客列表共同数据
    paginator = Paginator(blogs_all_list, settings.EACH_PAGE_BLOGS_NUMBER)  # 每十篇进行分页
    page_num = request.GET.get('page', 1)  # 获取页码参数 默认值为1 http://localhost:8000/blog/?page=2 输入键值对
    page_of_blogs = paginator.get_page(page_num)  # 获取具体页面,若page_num=其他字符，默认为1
    current_page_num = page_of_blogs.number  # 获取当前页码
    page_range = [i for i in
                  range(max(1, current_page_num - 2), min(current_page_num + 3, paginator.num_pages + 1))]
    # 增加省略号标记
    if page_range[0] - 1 >= 2:
        page_range.insert(0, '...')
    if paginator.num_pages - page_range[-1] >= 2:
        page_range.append('...')
    # 增加首页和尾页
    if page_range[0] != 1:
        page_range.insert(0, 1)
    if page_range[-1] != paginator.num_pages:
        page_range.append(paginator.num_pages)

    #   获取博客分类对应的数量
    '''blog_types = BlogType.objects.all()
    blog_types_list = []
    for blog_type in blog_types:
         blog_type.blog_count = Blog.objects.filter(blog_type=blog_type).count()    #绑定新的属性
         blog_types_list.append(blog_type)
    '''

    #   获取日期归档对应的博客数量
    blog_dates = Blog.objects.dates('created_time', 'month', order="DESC")
    for blog_date in blog_dates:
        blog_count = Blog.objects.filter(created_time__year=blog_date.year, created_time__month=blog_date.month).count()
        blog_dates_dict = {blog_date: blog_count, }
    context = {'blogs': page_of_blogs.object_list,  # 分页内所有博客
               'blog_types': BlogType.objects.annotate(blog_count=Count('blog')),  # 博客种类(包括对应的数量)
               'page_of_blogs': page_of_blogs,  # 指定博客页
               'page_range': page_range,  # 博客页码显示范围
               'blog_dates': blog_dates_dict,  # 博客创建时间
               }
    return context


def blog_list(request):
    #   所有博客列表
    blogs_all_list = Blog.objects.all()  # 分页器操作
    context = get_blog_list_common_date(request, blogs_all_list)
    return render(request, 'blog/blog_list.html', context)


def blogs_with_type(request, blog_type_pk):
    #   按照种类分类博客
    blog_type = get_object_or_404(BlogType, id=blog_type_pk)
    blogs_all_list = Blog.objects.filter(blog_type=blog_type)  # 分页器操作
    context = get_blog_list_common_date(request, blogs_all_list)
    context['blog_type'] = blog_type
    return render(request, 'blog/blogs_with_type.html', context)


def blogs_with_date(request, year, month):
    #   按照时间归档博客
    blogs_all_list = Blog.objects.filter(created_time__year=year, created_time__month=month)  # 分页器操作
    context = get_blog_list_common_date(request, blogs_all_list)
    context['blogs_with_date'] = '%s年%s月' % (year, month)  # 日期归档
    return render(request, 'blog/blogs_with_date.html', context)


def blog_detail(request, blog_id):
    context = {}
    blog = get_object_or_404(Blog, id=blog_id)
    read_cookie_key = read_statistics_once_read(request, blog)

    # filter的筛选条件//exclude 排除 与filter用法相反
    context['previous_blog'] = Blog.objects.filter(created_time__gt=blog.created_time).last()
    context['next_blog'] = Blog.objects.filter(created_time__lt=blog.created_time).first()
    context['blog'] = blog
    response = render(request, 'blog/blog_detail.html', context)  # 响应
    response.set_cookie(read_cookie_key, 'True')    #阅读cookie标记
    return response
