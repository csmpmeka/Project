from django.urls import path
from django.contrib.auth import views as auth_views

from home import views
from django.contrib.auth.decorators import login_required
from django.conf.urls.static import static

from second_sale import settings

urlpatterns = [
    path('home/', views.Home.as_view(), name='homepage'),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path("register/", views.Registration.as_view(), name='signup'),
    path('logout/', views.SignOutView.as_view(), name='logout'),
    path('post_ad/', login_required(views.PostAdvertisement.as_view()), name='post_ad'),
    path('product_lists/<int:category_id>/<int:page>/', views.GetProductList.as_view(), name='product_list'),
    path('product_details/<int:pk>/', views.ShowProductDetails.as_view(), name='product_details'),
    path('product_search/<int:page>/', views.SearchProduct.as_view(), name='product_search'),
    # path('recommendations/<int:user_id>/<int:product_id>/', views.GetRecommendations.as_view(),
    #      name="get_recommendations"),
    path('post_comment/<int:pk>/', views.PostComment.as_view(), name='post_comment'),
    path('dashboard/', views.Dashboard.as_view(), name='dashboard'),
    path('sold/<int:pk>', views.MarkSold.as_view(), name='sold'),
    path('delete_ad/<int:pk>', views.DeleteAd.as_view(), name='delete_ad')

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
