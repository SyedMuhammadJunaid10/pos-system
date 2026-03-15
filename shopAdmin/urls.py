from django.urls import path
from . import views
app_name='shops'
urlpatterns = [
    path('shop_dashboard/',views.shop_dashboard,name='shop_dashboard'),
    path('products/',views.shop_product,name='shop_product'),
    path('products/add/',views.add_product,name='add_product'),
    path('products/serach/',views.search_product,name='search_product'),
    path('shop_inventory/',views.shop_inventory,name='shop_inventory'),
    path('restock_product/',views.restock_product,name='restock_product'),
    path('manager/',views.shop_manager,name='shop_manager'),
    path('shop_sales/',views.shop_sales,name='shop_sales'),
    path('shop_report/',views.shop_report,name='shop_report'),
    path('generate_report/',views.generate_report,name='generate_report'),
    path('download_sales_excel/',views.download_sales_excel,name="download_sales_excel"),
    path('shop_setting/',views.shop_setting,name='shop_setting'),
    path('logout/',views.logout,name='logout')
    
    
]
