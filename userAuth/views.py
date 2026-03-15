from django.shortcuts import render,redirect
from django.contrib import messages
from firebase_admin import auth
from django.db import connection
from django.contrib.auth.hashers import make_password,check_password 
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse

#Registration
def register(request):
    if request.method=="POST":
        username=request.POST.get('username')
        email=request.POST.get('email')
        password=request.POST.get('password')
        confirmpassword=request.POST.get('confirmpassword')
        shopName=request.POST.get('shopname')
        shopCode=request.POST.get('shopcode')
        if password != confirmpassword:
            messages.error(request, "Passwords do not match")
            return redirect('register')
        
        try:
            # 1. Create user in Firebase
             firebase_user = auth.create_user(
                email=email,
                password=password
            )
            # 2. Send verification email
             verify_link = auth.generate_email_verification_link(email)
             
                #  Send email
             send_mail(
                subject="Verify your email",
                message=f"Click this link to verify your account:\n\n{verify_link}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=False,
            )
             
             print("Verification link:", verify_link)
             
             with connection.cursor() as cursor:
                cursor.execute("""
                            INSERT INTO shops (shop_name,shop_code,status) VALUES (%s,%s,%s) RETURNING id
                            """,[shopName,shopCode,'active']
                )
                print('shop data save')
                shop_row = cursor.fetchone()
                shop_id=shop_row[0]
                
                print("Shop ID:", shop_id)
                hashed_password = make_password(password)
                cursor.execute("""
                            INSERT INTO users (name,email,password,role,shop_id,status) VALUES (%s,%s,%s,'shop_admin',%s,%s)
                            """,[username,email,hashed_password,shop_id,True]
                )
                print('user data save')
             messages.success(request,'Registration successful. Verify your email.')
             return redirect('login')
                
        except Exception as e:
            messages.error(request,str(e))
            print("ERROR")

    return render(request,'register.html')


#Login 
def login(request):
    if request.method == 'POST':

        email = request.POST.get('username')
        password = request.POST.get('password')

        try:
            firebase_user = auth.get_user_by_email(email)

            if not firebase_user.email_verified:
                messages.error(request, "Please verify your email first.")
                return redirect("login")

            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT * FROM users WHERE email=%s
                """, [email])
                user = cursor.fetchone()

            if not user or not check_password(password, user[3]):
                messages.error(request, "Invalid email or password")
                return redirect('login')

            request.session.flush()
            request.session['id'] = user[0]
            request.session['role'] = user[4]
            request.session['shop_id'] = user[5]

            if user[4] == 'super_admin':
                return redirect('super:dashboard')
            elif user[4] == 'shop_admin':
                return redirect('shops:shop_dashboard')
            elif user[4] == 'cashier':
                return redirect('dashboard:cashier')

        except Exception as e:
            messages.error(request, "Login failed")
            print(e)

    return render(request, "login.html")
