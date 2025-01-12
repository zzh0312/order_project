from django.shortcuts import render
from.models import Article
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import permission_required, login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.urls import reverse

def article_list(request):
    query = request.GET.get('q')
    if query:
        articles = Article.objects.filter(Q(title__icontains=query) | Q(author__icontains=query))
    else:
        articles = Article.objects.all()
    paginator = Paginator(articles, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'article_list.html', {'page_obj': page_obj, 'query': query, 'user':request.user})

@login_required
def article_detail(request, article_id):
    article = get_object_or_404(Article, id=article_id)
    return render(request, 'article_detail.html', {'article': article})

@permission_required('yourappname.can_publish_article')
def publish_article(request):
    # 这里是发布文章的逻辑
    articles = Article.objects.all()
    return render(request, 'publish_article.html', {'articles': articles})


def custom_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')  # 重定向到首页，你可以修改为你需要的页面
        else:
            return render(request, 'login.html', {'error': '用户名或密码错误'})
    else:
        return render(request, 'login.html')


def profile_view(request):
    return render(request, 'profile.html')

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def add_article(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        author = request.POST.get('author')
        content = request.POST.get('content')
        category = request.POST.get('category')
        publish_date = request.POST.get('publish_date')
        article = Article(
            title=title,
            author=author,
            content=content,
            category=category,
            publish_date=publish_date
        )
        article.save()
        return HttpResponseRedirect(reverse('article_list'))
    else:
        return render(request, 'add_article.html')
@login_required
def edit_article(request):
    article_id = request.GET.get('article_id')
    article = Article.objects.get(id = article_id)
    if request.method == 'POST':
        # 获取表单数据并更新文章对象
        article.title = request.POST.get('title')
        article.content = request.POST.get('content')
        article.author = request.POST.get('author')
        article.category = request.POST.get('category')
        article.publish_date = request.POST.get('publish_date')
        article.save()
        return redirect('article_list')
    else:
        return render(request, 'edit_article.html', {'article': article})
@login_required
def delete_article(request):
    article_id = request.GET.get('article_id')
    article = Article.objects.get(id = article_id)
    article.delete()
    return redirect('article_list')

def home(request):
    return render(request, 'home.html')