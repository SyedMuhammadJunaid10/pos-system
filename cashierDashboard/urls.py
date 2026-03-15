from django.urls import path
from . import views

app_name='dashboard'
urlpatterns = [
    path('cashierdashboard/',views.cashier,name='cashier'),
    path('enterbarcode/',views.Enter_barcode,name='Enter_barcode'),
    path('checkout/',views.payment_process,name='payment_process')
    
    
]
