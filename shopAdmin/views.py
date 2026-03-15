from django.shortcuts import render,redirect
from django.http import JsonResponse,HttpResponse
import barcode
from barcode.writer import ImageWriter
from django.db import connection
from django.conf import settings
import os, random
from django.contrib import messages
from functools import wraps
import openpyxl



def shopAdmin_require(f):
  @wraps(f)
  def wrapper(request,*args, **kwargs):
      if not request.session.get("id"):
          messages.error(request,'PLease Login First!')
          return redirect('auth:login')
      if request.session.get('role')!= 'shop_admin':
            messages.error(request, "Access denied")
            return redirect('auth:login')
      return f(request,*args, **kwargs)
  return wrapper
    



def generate_barcode(code):
    #generate barcode format
    Barcode=barcode.get_barcode_class('code128')
    
    #create folder to save image of barcode
    folder=os.path.join(settings.MEDIA_ROOT, 'barcodeImg')
    os.makedirs(folder, exist_ok=True)
    
    #path for save image
    file_path=os.path.join(folder,code)
    #generate barcode and save image
    Barcode(code, writer=ImageWriter()).save(file_path)
    
    return f'barcodeImg/{code}.png'

@shopAdmin_require
def shop_dashboard(request):
    shop_id=request.session.get('shop_id')
    user_id=request.session.get('id')
    #shop name
    with connection.cursor() as cur:
        cur.execute("SELECT shop_name FROM users LEFT JOIN shops ON  users.shop_id= shops.id WHERE shop_id=%s",[shop_id])
        shopName=cur.fetchone()[0]
        
    #set revenue and total order
    with connection.cursor() as cur:
        cur.execute('SELECT SUM(total_amount),COUNT(id) FROM sales WHERE shop_id=%s',[shop_id])
        revenue,total_order=cur.fetchone()
        
    #check low stock  
    with connection.cursor() as cur:
        cur.execute('SELECT COUNT(id) FROM products WHERE shop_id=%s and stock <= %s',[shop_id,50])
        lowStock=cur.fetchone()[0]
        
    #recent sale    
    with connection.cursor() as cur:
        cur.execute('SELECT id,total_amount,created_at FROM sales WHERE shop_id=%s ORDER BY created_at DESC LIMIT 5',[shop_id])
        sales=cur.fetchall()
        
        recent_sale=[
            {
                "id":r[0],
                "totalAmount":r[1],
                "time":r[2],
                }
            for r in sales
        ]
    
    #Alert For Low Stock
    with connection.cursor() as cur:
        cur.execute('SELECT product_name,stock FROM products WHERE shop_id=%s AND stock <=%s',[shop_id,50])
        stock=cur.fetchall()
        AlertStock=[]
        for s in stock:
            stock_level = "critical" if s[1] <= 20 else "warning"
            AlertStock.append({
                "name":s[0],
                "stock":s[1],
                "level":stock_level
            })
        
        
    return render(request,'shop_dashboard.html',{"shopname":shopName,
                                                 "revenue":int(revenue),
                                                 "total_order":total_order,
                                                 "lowStock":lowStock,
                                                 "recent_sale":recent_sale,
                                                 "AlertStock":AlertStock})

@shopAdmin_require
def shop_product(request):
    shop_id=request.session.get('shop_id')
    with connection.cursor() as cursor:
     cursor.execute("SELECT * FROM products WHERE shop_id=%s",[shop_id])
     rows=cursor.fetchall()
    products = []
    for r in rows:
        products.append({
            'shop_id': r[1],
            'name': r[2],
            'description': r[3],
            'cost': r[4],
            'price': r[5],
            'stock': r[6],
            'status': r[9],
            'category': r[11],
            'tax': r[12],
        })
    return render(request,'shop_product.html',{'products':products})

@shopAdmin_require
def add_product(request):
    if request.method == "POST":

        product_name = request.POST.get("productName")
        product_category = request.POST.get("productCategory")
        product_status = request.POST.get("productStatus")
        product_selling_price = request.POST.get("ProductsellingPrice")
        product_cost_price = request.POST.get("productCostPrice")
        product_stock = request.POST.get("productStock")
        product_tax = request.POST.get("productTax")
        product_des = request.POST.get("productDescription")

        shop_id = request.session.get('shop_id')   

        print(shop_id)
        barcode_value = f"PRD{shop_id}{random.randint(100000,999999)}"
        barcode_path = generate_barcode(barcode_value)

        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO products 
                (shop_id,product_name, description, cost_price, selling_price,
                 stock, barcode, barcode_image, status, category, tax_percent)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """, [
                shop_id,
                product_name,
                product_des,
                product_cost_price,
                product_selling_price,
                product_stock,
                barcode_value,
                barcode_path,
                product_status,
                product_category,
                product_tax
            ])
            print("Data Save!")

        messages.success(request, "Product saved successfully!")
        return redirect('shops:shop_product')
   
    return render(request, 'shop_product.html')

@shopAdmin_require
def search_product(request):
    shop_id=request.session.get('shop_id')
    serachProduct=request.GET.get("searchProducts")
    with connection.cursor() as cursor:
        cursor.execute("SELECT id,product_name,category,selling_price,cost_price,stock FROM products WHERE LIKE %s AND shop_id=%s",[serachProduct,shop_id])
        search=cursor.fetchall()
        
    # Convert tuples to dicts
    products_list = [
        {"id": p[0], "name": p[1],"category": p[2], "sellingPrice": float(p[3]),"costPrice": float(p[4]), "stock": p[5]}
        for p in search
    ]
    return JsonResponse({"product":products_list})


@shopAdmin_require
def shop_inventory(request):
    shop_id = request.session.get('shop_id')

    with connection.cursor() as cur:
        # Low stock products
        cur.execute(
            "SELECT * FROM products WHERE shop_id=%s AND stock <= 50",
            [shop_id]
        )
        lowStock = cur.fetchall()

        lowStocks = [{
            'id': ls[0],
            'name': ls[2],
            'stock': ls[6]
        } for ls in lowStock]

        # All products for dropdown
        cur.execute(
            "SELECT id, product_name FROM products WHERE shop_id=%s",
            [shop_id]
        )
        products = cur.fetchall()
        # Total product
        cur.execute("SELECT COUNT(*) FROM products WHERE shop_id=%s",[shop_id])
        totalProduct=cur.fetchone()[0]
        
        #Low stock
        cur.execute('SELECT COUNT(id) FROM products WHERE shop_id=%s and stock <= %s',[shop_id,50])
        lowStock=cur.fetchone()[0]
        
        #Out of Stock
        cur.execute('SELECT COUNT(id) FROM products WHERE shop_id=%s and stock <= %s',[shop_id,10])
        outStock=cur.fetchone()[0]
        
        #Inventory Value
        cur.execute('SELECT SUM(selling_price) FROM products WHERE shop_id=%s',[shop_id])
        inventoryValue=cur.fetchone()[0]
        
    return render(request, 'shop_inventory.html', {
        'lowStocks': lowStocks,
        'products': products,
        "totalProduct":totalProduct,
        "lowStock":lowStock,
        "outStock":outStock,
        "inventoryValue":int(inventoryValue)
        
    })

@shopAdmin_require
def restock_product(request):
    if request.method == "POST":
        shop_id = request.session.get('shop_id')
        
        productId=request.POST.get("productName")
        quantity = request.POST.get("quantity")
        supplierName = request.POST.get("supplierName")
        costPrice = request.POST.get("costPrice")
        managerName = request.POST.get("managerName")
        description = request.POST.get("description")
        
        # print(f"product name {productId}")
        # print(f"product quntity {quantity}")
        
        
        if shop_id:
            with connection.cursor() as cur:
                cur.execute("""
                    UPDATE products
                    SET stock = stock + %s
                    WHERE id = %s AND  shop_id = %s
                """, [quantity, productId,shop_id])
                messages.success(request,"Product Stock Increase Succesfully!")
        else:
            print('Error!')

        return redirect('shops:shop_inventory') 
    return render(request,'shop_inventory.html')




@shopAdmin_require
def shop_sales(request):
    shop_id = request.session.get('shop_id')
    # print(shop_id)
    with connection.cursor() as cur:
        cur.execute("SELECT st.quantity,st.price,s.payment_method,s.created_at FROM sale_items st JOIN products p ON st.product_id=p.id  JOIN sales s ON st.sale_id=s.id WHERE s.shop_id=%s",[shop_id])
        row=cur.fetchall()
        sales=[
            {
            "item":s[0],
            "price":s[1],
            "pay_Method":s[2],
            "time":s[3]
        } 
            for s in row ]
        # print(sales)
    
    return render(request,'shop_sales.html',{"sales":sales})

@shopAdmin_require
def shop_manager(request):
    return render(request,'manager.html')

@shopAdmin_require
def shop_setting(request):
    return render(request,'shop_setting.html')

@shopAdmin_require
def shop_report(request):
   

    return render(request, 'shop_report.html')

@shopAdmin_require
def generate_report(request):
    shop_id = request.session.get('shop_id')
    reports = None

    if request.method == "POST":
        first_date = request.GET.get('firstDate')
        second_date = request.GET.get('secondDate')

        with connection.cursor() as cur:
            cur.execute("""
                SELECT id,payment_method,total_amount,created_at  FROM sales 
                WHERE created_at BETWEEN %s AND %s
                AND shop_id=%s
                ORDER BY created_at DESC 
            """, [first_date, second_date,shop_id])

            reports = cur.fetchall()

        if reports:
            messages.success(request, "Report generated successfully!")
           
        else:
            messages.warning(request, "No sales found in this date range.")

    return render(request, 'shop_report.html', {"reports": reports})

@shopAdmin_require
def download_sales_excel(request):

    shop_id = request.session.get('shop_id')
    first_date = request.GET.get('firstDate')
    second_date = request.GET.get('secondDate')

    with connection.cursor() as cur:
        cur.execute("""
            SELECT id,payment_method,total_amount,created_at
            FROM sales
            WHERE created_at BETWEEN %s AND %s
            AND shop_id = %s
            ORDER BY created_at DESC
        """, [first_date, second_date, shop_id])

        reports = cur.fetchall()

    # Create Excel
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Sales Report"

    headers = ["Sale ID", "Customer", "Total Amount", "Date"]
    ws.append(headers)

    total_sales = 0

    for row in reports:
        ws.append(row)
        total_sales += row[2]

    ws.append(["", "", "Total Sales", total_sales])

    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    response['Content-Disposition'] = 'attachment; filename="sales_report.xlsx"'

    wb.save(response)

    return response



@shopAdmin_require
def logout(request):
    request.session.flush()
    messages.success(request,'Successfully Logout!')
    return redirect('auth:login')
