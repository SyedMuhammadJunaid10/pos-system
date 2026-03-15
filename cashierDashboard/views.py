from django.shortcuts import render,redirect
from django.db import  connection
from django.http import JsonResponse
import json
from django.contrib import messages
from functools import wraps
from django.db import transaction

def cashier_require(f):
    @wraps(f)
    def wrapper(request,*args, **kwargs):
      if not request.session.get("id"):
          messages.error(request,'PLease Login First!')
          return redirect('auth:login')
      if request.session.get('role')!= 'cashier':
            messages.error(request, "Access denied")
            return redirect('auth:login')
      return f(request,*args, **kwargs)
    return wrapper
            
    




# Create your views here.
@cashier_require
def cashier(request):
    id=request.session.get('id')
    role=request.session.get('role')
    # print(role)
    print(id)
    with connection.cursor() as cursor:
        cursor.execute('SELECT shop_name FROM shops WHERE id=%s',[id])
        row=cursor.fetchone()
        shopName=row[0] if row else 'Admin cashier'
        
        cursor.execute('SELECT name FROM users WHERE id=%s',[id])
        r=cursor.fetchone()
        cashierName=r[0] if r else 'undefined'
        
        
        
    return render(request,'cashierDashboard.html',{"shopName":shopName,"cashierName":cashierName})

@cashier_require
def Enter_barcode(request):
    barcode = request.GET.get('barcode')
    print(barcode)
    with connection.cursor() as cursor:
        cursor.execute('SELECT id,shop_id,product_name,selling_price,stock,tax_percent,category,barcode_image FROM products WHERE barcode=%s',[barcode])
        product=cursor.fetchone()
        
    if product:
            return JsonResponse({
                "id":product[0],
                'shop_id':product[1],
                "name":product[2],
                "price":float(product[3]),
                "stock":product[4],
                "tax":product[5],
                "barcode":barcode,
                "category":product[6],
                "image":product[7]
                
            })
    return JsonResponse({'error':'Product Not Found!'},status=404)



#fetch payment sucess data as a json format
@cashier_require    
def payment_process(request):
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    shop_id = request.session.get('shop_id')
    user_id = request.session.get('id')

    data = json.loads(request.body)
    print(data.get('product_id'))
    cart=data.get('cart',[])
    if not cart:
    
        return JsonResponse({"status": "error", "message": "Cart empty"}, status=400)
    for item1 in cart:
        print(item1)
    # print(cart)

    try:
        with transaction.atomic():  
            with connection.cursor() as cur:
                # Insert into sales table
                cur.execute("""
                    INSERT INTO sales (shop_id, user_id, total_amount, payment_method)
                    VALUES (%s, %s, %s, %s)
                    RETURNING id
                """, [shop_id, user_id, data["total"], data["payment_method"]])
                sale_id = cur.fetchone()[0]
                print("sale data is save",sale_id)
                print("NOT ENTER")
                # Insert each cart item 
                for item in cart:
                    print(item)
                    product_id = item.get("product_id")

                    if not product_id:
                        raise Exception("Product ID missing in cart")
                    

                    quantity = item.get("quantity", 1)
                    price = item.get("price", 0)

                    cur.execute("""
                        INSERT INTO sale_items (sale_id, product_id, quantity, price)
                        VALUES (%s, %s, %s, %s)
                    """, [sale_id, product_id, quantity, price])
                    print("Data save in item!")
                
                #reduce stock in the product
                    cur.execute("""
                        UPDATE  products SET stock=stock - %s WHERE id = %s
                        """,[quantity,product_id])
                    
        return JsonResponse({
            "status": "success",
            "sale_id": sale_id
            })

    except Exception as e:
        #  shows full DB error
        import traceback
        print(traceback.format_exc())   
        return JsonResponse({"error": str(e)}, status=500)


        


    