from django.shortcuts import render
from .models import Post
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger, InvalidPage
import markdown
from django.views.generic import ListView
from django.http import Http404
from .forms import EmailPostForm
from django.core.mail import send_mail
from django.views.decorators.http import require_POST


def post_share(request, post_id):
    post = get_object_or_404(Post, id=post_id, status=Post.Status.PUBLISHED)
    sent = False
    if request.method == 'POST':
        form = EmailPostForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject = f"{cd['name']} recommends you read " \
                      f"{post.title}"
            message = f"Read {post.title} at {post_url}\n\n" \
                      f"{cd['name']}\'s comments: {cd['comments']}"
            send_mail(subject, message, 'ajohnribanodev1@gmail.com',
                      [cd['to']])
            sent = True
    else:
        form = EmailPostForm()
    return render(request, 'blog/post/share.xhtml', {'post': post,
                                                     'form': form,
                                                     'sent': sent})


class PostListView(ListView):
    """Alternative to function based view for post list"""
    queryset = Post.published.all()
    context_object_name = 'posts'
    paginate_by = 3
    template_name = 'blog/post/list.xhtml'

    def get_template_names(self):
        if self.request.GET.get('page') and not self.request.GET.get('page').isdigit():
            raise Http404
        if getattr(self, 'page_not_found', False):
            return ['404.html']
        return [self.template_name]
    
    def paginate_queryset(self, queryset, page_size):
        """
        Paginate the queryset, and handle potential 404 errors.
        """
        paginator = self.get_paginator(
            queryset, page_size, orphans=self.get_paginate_orphans(),
            allow_empty_first_page=self.get_allow_empty())
        page_kwarg = self.page_kwarg
        page = self.kwargs.get(page_kwarg) or self.request.GET.get(page_kwarg) or 1
        try:
            page_number = int(page)
        except ValueError:
            if page == 'last':
                page_number = paginator.num_pages
            else:
                # Raise a 404 for non-integer page numbers *before* EmptyPage
                self.page_not_found = True  # Set the flag
                return (paginator, None, [], False) # Return to avoid raising the original exception.
                # raise Http404("Invalid page number.") # Better place for Http404

        try:
            page = paginator.page(page_number)
            return (paginator, page, page.object_list, page.has_other_pages())
        except InvalidPage as e:
             # Set the flag for get_template_names()
            self.page_not_found = True
             #Return to avoid raising EmptyPage
            return (paginator, None, [], False)

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