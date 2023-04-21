import datetime
import random

import requests
from django.contrib import messages
from django.contrib.auth import logout, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect

from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from home.forms import UserForm
from home.models import Advertisement, Category, Comments, Replies, UserRating


class Home(View):
    def get(self, request):
        latest_ads = Advertisement.objects.all().order_by('id').reverse()[0:12]
        premium_ads = Advertisement.objects.filter(premium_ad=True).order_by('id').reverse()[0:2]
        categories = Category.objects.all()
        return render(request,
                      context={'latest_ads': latest_ads,
                               'premium_ads': premium_ads,
                               'categories': categories},
                      template_name='home.html')


class Registration(View):
    def get(self, request):
        form = UserForm()
        return render(request=request,
                      template_name="registration/signup.html",
                      context={"register_form": form})

    def post(self, request):
        form = UserForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Successfully registered")
            return redirect("login")
        messages.error(request, "Registration failed. Please try again!")
        return render(request=request,
                      template_name="registration/signup.html",
                      context={"form": form})


class SignOutView(View):
    def get(self, request):
        logout(request)
        return HttpResponseRedirect('/login')


@method_decorator(csrf_exempt, name='dispatch')
class PostAdvertisement(View):
    def get(self, request):
        return render(request=request,
                      template_name="post_ad.html"
                      )

    def post(self, request):
        title = request.POST.get('title', 'samsung s23')
        used_for = request.POST.get('used_for', '1 Year')
        negotiable = request.POST.get('negotiable', False)
        category_name = request.POST.get('category', 'Electronics')
        if category_name == 'Apparels':
            category_name = 'Apparels & Accessories'
        category = Category.objects.get(name=category_name)
        state = request.POST.get('status', 'Used')
        description = request.POST.get('description', 'No text')
        posted_by = request.user  # request.user
        posted_on = datetime.datetime.now()
        product_image = request.FILES['file']
        price = float(request.POST.get('price', '0'))
        premium_ad = False
        warranty = request.POST.get('warranty', 'None')
        ad_obj = Advertisement.objects.create(title=title, used_for=used_for, negotiable=negotiable,
                                              category=category, state=state, description=description,
                                              posted_by=posted_by, posted_on=posted_on, price=price,
                                              premium_ad=premium_ad, warranty=warranty, product_image=product_image
                                              )
        category.total_ads += 1
        ad_obj.save()
        category.save()
        return render(request=request,
                      template_name="post_ad.html",
                      context={"message": "successfully published your advertisement"}
                      )


@method_decorator(csrf_exempt, name='dispatch')
class PostComment(View):
    def post(self, request, pk):
        advertisement_obj = Advertisement.objects.get(id=pk)
        comment = request.POST.get('comment')
        comment_obj = Comments(
            product=advertisement_obj,
            description=comment,
            posted_on=datetime.datetime.now(),
            posted_by=request.user
        )
        comment_obj.save()
        return redirect('product_details', pk=f'{advertisement_obj.id}')


class PostRelies(View):
    def post(self, request, comment_id):
        comment = Comments.objects.get(id=comment_id)
        reply = Replies(
            comment=comment,
            posted_by=request.user,
            description=request.POST.get('reply'),
            posted_on=datetime.datetime.now()
        )
        return redirect('product_details')


class GetProductList(View):
    def get(self, request, category_id, page=1):
        category = Category.objects.get(id=category_id)
        products = Advertisement.objects.filter(category=category).order_by("views")
        paginator = Paginator(products, per_page=8)
        paginated_products = paginator.get_page(page)
        return render(request=request,
                      context={'category_id': category.id,
                               'category_title': category.name,
                               'products': paginated_products.object_list,
                               'page_obj': paginated_products,
                               },
                      template_name="product_list.html")


class ShowProductDetails(View):
    def get(self, request, pk):
        comment_to_replies = []
        item = Advertisement.objects.get(id=pk)
        Advertisement.objects.filter(id=pk).update(views=item.views + 1)
        recommendation_ids = GetRecommendations.get_recommendations(user_id=request.user.id, product_id=item.id)
        # recommendations = Advertisement.objects.filter(id__in=recommendation_ids).order_by("views")
        recommendations = Advertisement.objects.all().order_by("views")[0:5]
        if request.user.is_authenticated:
            user_rating = UserRating.objects.filter(
                Q(advertisement=item) & Q(user=request.user)).first()

            if user_rating:
                user_rating.num_of_clicks += 1
                user_rating.save()
            else:
                user_rating = UserRating(
                    advertisement=item,
                    user=request.user,
                    num_of_clicks=1,
                )
                user_rating.save()
        comments = Comments.objects.filter(product=item).order_by('id')
        for comment in comments:
            replies = Replies.objects.filter(comment=comment).order_by('id')
            comment_to_replies.append({comment: replies})
        return render(request=request,
                      context={'item': item,
                               'comments': comment_to_replies,
                               'recommendations': recommendations},
                      template_name="product_detail.html")


@method_decorator(csrf_exempt, name='dispatch')
class SearchProduct(View):
    def get(self, request, page=1):
        query = request.GET.get('q')
        products = Advertisement.objects.filter(Q(title__icontains=query) | Q(description__icontains=query))
        paginator = Paginator(products, per_page=8)
        paginated_products = paginator.get_page(page)
        return render(request=request,
                      context={
                          'products': paginated_products.object_list,
                          'page_obj': paginated_products,
                      },
                      template_name="search_list.html")


@method_decorator(login_required, name='dispatch')
class Dashboard(View):
    def get(self, request):
        user = User.objects.get(id=request.user.id)
        ads_posted = Advertisement.objects.filter(posted_by=user)
        sold_ads = ads_posted.filter(sold=True).all()
        live_ads = ads_posted.filter(sold=False).all()
        total_ads = ads_posted.all()

        return render(
            request=request,
            context={
                'user': user,
                'ads': total_ads,
                'total_ads': len(ads_posted.all()),
                'sold_ads': len(sold_ads.all()),
                'live_ads': len(live_ads.all())
            },
            template_name='dashboard.html'
        )


class MarkSold(View):
    def get(self, request, pk):
        ad = Advertisement.objects.get(id=pk)
        ad.sold = True
        ad.save()
        return redirect('dashboard')


class DeleteAd(View):
    def get(self, request, pk):
        Advertisement.objects.get(id=pk).delete()
        return redirect('dashboard')


class GetRecommendations(View):
    @staticmethod
    def get_recommendations(user_id, product_id):
        try:
            URL = "http://localhost:8001/recommendations"
            PARAMS = {'user_id': user_id,
                      'product_id': product_id}
            r = requests.get(url=URL, params=PARAMS)
            data = r.json()
        except:
            data= random.randint(30)
        return data
