from django.shortcuts import render
from .models import Post
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator
import markdown

def post_list(request):
    post_list = Post.published.all()
    # Pagination
    paginator = Paginator(post_list, 3)
    page_number = request.GET.get('page', 1)
    posts = paginator.page(page_number)
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