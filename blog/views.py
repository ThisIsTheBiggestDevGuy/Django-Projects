from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from .models import Post, Comment
from .forms import CommentForm
from django.contrib.auth.models import User
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

# the function below, was the first hoem view created, made it a comment, just in case.
#def home(request):
    #context = {
        #'posts': Post.objects.all()
    #}
    #return render(request,'blog/home.html', context)

class PostListView(ListView):
    model = Post
    template_name = 'blog/home.html' # <app>/<model> _ <viewtype>.html
    context_object_name = 'posts'
    ordering = ['-date_posted']
    paginate_by = 4

@method_decorator(login_required, name='dispatch')
class LoggedInUserPostListView(ListView):
    model = Post
    template_name = 'blog/logged_in_user_posts.html'
    context_object_name = 'posts'
    paginate_by = 2
    def get_queryset(self):
        user = self.request.user
        return Post.objects.filter(author=user).order_by('-date_posted')

@method_decorator(login_required, name='dispatch')
class UserCommentsView(ListView):
    model = Comment
    template_name = 'blog/user_comments.html'
    context_object_name = 'comments'
    paginate_by = 2

    def get_queryset(self):
        user = self.request.user
        return Comment.objects.filter(author=user).order_by('-created_at')    

class UserPostListView(ListView):
    model = Post
    template_name = 'blog/user_posts.html' # <app>/<model> _ <viewtype>.html
    context_object_name = 'posts'
    paginate_by = 2
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['username'] = self.kwargs.get('username')
        return context
    
    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        return Post.objects.filter(author=user).order_by('-date_posted')


from django.views.generic import DetailView
from django.shortcuts import get_object_or_404, redirect
from .models import Post, Comment
from .forms import CommentForm

class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/post_detail.html'
    context_object_name = 'post'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comment_form'] = CommentForm()  # Add the CommentForm to the context
        return context

    def post(self, request, *args, **kwargs):
        post = self.get_object()
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.author = request.user
            comment.post = post
            comment.save()
            messages.info(self.request,'comment successfully sent')
            return redirect(post.get_absolute_url())
        else:
            # If the form is not valid, re-render the template with the errors
            context = self.get_context_data(**kwargs)
            context['comment_form'] = comment_form
            return self.render_to_response(context)

    
class PostCreateView(LoginRequiredMixin,CreateView):
    model = Post
    fields = ['title', 'content']
    def form_valid(self, form):
        form.instance.author = self.request.user
        messages.success(self.request, 'Post successfully sent')
        return super().form_valid(form)


class PostUpdateView(LoginRequiredMixin,UserPassesTestMixin,UpdateView):
    model = Post
    fields = ['title', 'content']
    def form_valid(self, form):
        form.instance.author = self.request.user
        messages.success(self.request, 'Post successfully sent')
        return super().form_valid(form)
    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False

class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin,DeleteView):
    model = Post
    success_url = '/'
    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False
class CommentUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Comment
    fields = ['content']
    def get_success_url(self):
        return self.object.post.get_absolute_url()
    def test_func(self):
        comment = self.get_object()
        return self.request.user == comment.author
class CommentDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Comment
    def get_success_url(self):
        return self.object.post.get_absolute_url()
    def test_func(self):
        comment = self.get_object()
        return self.request.user == comment.author
    

def about(request):
    context = {
        'title': 'About'
    }
    return render(request,'blog/about.html', context)



