from django.shortcuts import render,redirect
from django.contrib import messages
from django.db import connection
from django.contrib.auth.hashers import make_password
from django.core.mail import send_mail
from django.conf import settings
from firebase_admin import auth
from functools import wraps


def superAdmin_Require(f):
    @wraps(f)
    def wrapper(request,*args, **kwargs):
      if not request.session.get("id"):
          messages.error(request,'PLease Login First!')
          return redirect('auth:login')
      if request.session.get('role')!= 'super_admin':
            messages.error(request, "Access denied")
            return redirect('auth:login')
      return f(request,*args, **kwargs)
    return wrapper
            

@superAdmin_Require
def dashboard(request):
    with connection.cursor() as cursor:
        #Active & INactive Shops
        cursor.execute("SELECT COUNT(*) from shops WHERE status='active'") 
        activeShop=cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) from shops WHERE status='inactive'") 
        InactiveShop=cursor.fetchone()[0]
        
        #REVENUE
    with connection.cursor() as cursor:
        cursor.execute("SELECT SUM(total_amount) from sales") 
        revenue=cursor.fetchone()[0]
    #Total Order  
    context={
            'active':activeShop,
            'inactive':InactiveShop,
            'revenue':int(revenue)
        }
        
    return render(request,'dashboard.html',context)

@superAdmin_Require
def shop(request):
    with connection.cursor() as cursor:
        cursor.execute("SELECT * from shops") 
        shopDetails=cursor.fetchall()
    return render(request,'shop.html',{"shopDetails":shopDetails})

@superAdmin_Require
#add shop 
def add_shop(request):
    if request.method == "POST":
        
        shopName = request.POST.get('shopName')
        shopCategory = request.POST.get('shopCategory')
        shopCode = request.POST.get('shopCode')
        shopOwner = request.POST.get('shopOwner')
        mobileNum = request.POST.get('mobileNum')
        email = request.POST.get('email')
        shopLocation = request.POST.get('shopLocation')
        status = request.POST.get('status')

        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO shops 
                    (shop_name, shop_code, status, owner_name, email, shoplocation, mobile, category)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
                """, [
                    shopName, shopCode, status, shopOwner,
                    email, shopLocation, mobileNum, shopCategory
                ])

            messages.success(request, "Shop added successfully 🎉")
            return redirect('super:shop')

        except Exception as e:
            messages.error(request, str(e))

    return render(request, 'shop.html')

@superAdmin_Require
#DELETE Shop
def delete_shop(request,shop_id):
    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM shops WHERE id=%s",[shop_id])
           
    messages.success(request, "Shop DELETED successfully 🎉")    
    return redirect('super:shop')


@superAdmin_Require
def setting(request):
    return render(request,'setting.html')

@superAdmin_Require
def report(request):
    return render(request,'report.html')


#user where add user in user table

@superAdmin_Require
def user(request):
    # Fetch active shops
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT id, shop_name 
            FROM shops 
            WHERE status = 'active'
        """)
        shops = cursor.fetchall()

    if request.method == "POST":
        firstName = request.POST.get('userFirstName')
        secondName = request.POST.get('userSecondName')
        username = firstName + " " + secondName
        email = request.POST.get('userEmail')
        shop_id = request.POST.get('selectShop')
        role = request.POST.get('userRole')
        password = request.POST.get('userPassword')
        confirmpassword = request.POST.get('userConPassword')
        status = request.POST.get('userStatus')
        shop_id=int(shop_id)
 
        # Check password match
        if password != confirmpassword:
            messages.error(request, "Passwords do not match")
            return redirect('super:user')

        try:
            #  Create user in Firebase
            firebase_user = auth.create_user(
                email=email,
                password=password
            )

            #  Generate verification link
            verify_link = auth.generate_email_verification_link(email)

            #  Send verification email
            send_mail(
                subject="Verify your email",
                message=f"Click this link to verify your account:\n\n{verify_link}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=False,
            )

            # print("Verification link:", verify_link)
            # print(shop_id)

            #  Save user in PostgreSQL
            hashed_password = make_password(password)
            with connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO users (name,email,password,role,shop_id,status)
                    VALUES (%s,%s,%s,%s,%s,%s)
                """, [username, email, hashed_password, role, shop_id, status])
                print('User data saved')

            messages.success(request, 'Registration successful. Verify your email.')
            return redirect('auth:login')

        except Exception as e:
            messages.error(request, str(e))
            print("ERROR:", e)
    
    with connection.cursor() as cursor:
        cursor.execute("SELECT u.* , s.shop_name FROM users u LEFT JOIN shops s ON u.shop_id = s.id")
        rows=cursor.fetchall()
        
        users=[]
        for r in rows:
            users.append({
            'id': r[0],
            'name': r[1],
            'email': r[2],
            'role': r[4],
            'shop_id': r[5],
            'status': r[6],
            'created': r[7],
            'shop_name':r[8]
           
        })
        
    return render(request, 'user.html', {'shops': shops,'users':users})



@superAdmin_Require
def logout(request):
    messages.success(request,'Successfully Logout!')
    return redirect('auth:login')

