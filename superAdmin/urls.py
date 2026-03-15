from django.urls import path
from . import views
app_name='super'
urlpatterns = [
    path('Dashboard/',views.dashboard,name="dashboard"),
    path('report/',views.report,name="report"),
    path('shop/',views.shop,name="shop"),
    path('delete_shop/<int:shop_id>/',views.delete_shop,name='delete_shop'),
    path('add_shop/',views.add_shop,name="add_shop"),
    path('user/',views.user,name="user"),
    path('setting/',views.setting,name="setting"),
    path('logout/',views.logout,name="logout")
    
    
]
