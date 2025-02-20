from django.shortcuts import render
from .models import Post
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import markdown
from django.views.generic import ListView


class PostListView(ListView):
    """Alternative to function based view for post list"""
    queryset = Post.published.all()
    context_object_name = 'posts'
    paginate_by = 3
    template_name = 'blog/post/list.xhtml'

def post_list(request):
    post_list = Post.published.all()
    # Pagination
    paginator = Paginator(post_list, 3)
    page_number = request.GET.get('page', 1)
    try:
        posts = paginator.page(page_number)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)
    return render(request,
                  'blog/post/list.xhtml',
                  {'posts': posts})

def post_detail(request, year, month, day, post):
    md = markdown.Markdown(extensions=["fenced_code"])
    post = get_object_or_404(Post,
                            status=Post.Status.PUBLISHED,
                            slug=post,
                            publish__year=year,
                            publish__month=month,
                            publish__day=day
                            )
    post.body = md.convert(post.body)
    return render(request,
                  'blog/post/detail.xhtml',
                  {'post': post})