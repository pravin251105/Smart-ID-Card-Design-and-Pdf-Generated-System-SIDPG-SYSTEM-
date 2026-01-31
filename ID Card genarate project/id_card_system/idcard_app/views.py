from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from django.http import HttpResponseForbidden
from datetime import datetime

from .models import User, DashboardSettings
from .models import TemplateDesign
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.http import require_POST
import json
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from .models import IDTemplate


# =========================
# ADMIN CHECK FUNCTION
# =========================
def is_admin(user):
    return user.is_authenticated and (user.is_superuser or getattr(user, "role", "") == "admin")


# =========================
# ADMIN DECORATOR
# =========================
def admin_required(view_func):
    def wrapper(request, *args, **kwargs):
        if is_admin(request.user):
            return view_func(request, *args, **kwargs)
        return HttpResponseForbidden("Admin access only")
    return wrapper


# =========================
# LOGIN
# =========================
def login_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        user = authenticate(request, email=email, password=password)

        if user is None:
            messages.error(request, "Invalid Email or Password")
            return redirect("login")

        login(request, user)

        if is_admin(user):
            return redirect("admin_dashboard")
        else:
            return redirect("user_dashboard")

    return render(request, "idcard_app/login.html")


# =========================
# LOGOUT
# =========================
def logout_view(request):
    logout(request)
    return redirect("login")


# =========================
# USER DASHBOARD
# =========================
@login_required
def user_dashboard(request):
    # Get user and dashboard settings
    user = request.user
    try:
        settings = DashboardSettings.objects.first()
    except:
        settings = None
    
    def parse_date(value):
        if not value:
            return None
        try:
            return datetime.strptime(value, "%Y-%m-%d").date()
        except ValueError:
            return None

    if request.method == "POST":
        user.first_name = request.POST.get("first_name", user.first_name)
        user.last_name = request.POST.get("last_name", user.last_name)
        user.phone = request.POST.get("phone", user.phone)
        user.emergency_mobile = request.POST.get("emergency_mobile", user.emergency_mobile)
        user.department = request.POST.get("department", user.department)
        user.roll_no = request.POST.get("roll_no", user.roll_no)
        user.blood_group = request.POST.get("blood_group", user.blood_group)
        user.address = request.POST.get("address", user.address)
        user.residence_status = request.POST.get("residence_status") or None

        age_val = request.POST.get("age")
        try:
            user.age = int(age_val) if age_val else None
        except ValueError:
            user.age = user.age

        user.date_of_birth = parse_date(request.POST.get("date_of_birth"))
        user.valid_upto = parse_date(request.POST.get("valid_upto"))

        if "photo" in request.FILES:
            user.photo = request.FILES["photo"]
        if "signature" in request.FILES:
            user.signature = request.FILES["signature"]

        user.save()
        messages.success(request, "Profile updated successfully.")
        return redirect("user_dashboard")
    
    return render(request, "idcard_app/user_dashboard.html", {
        "user": user,
        "settings": settings
    })


# =========================
# ADMIN DASHBOARD
# =========================
@login_required
@admin_required
def admin_dashboard(request):

    # dashboard stats sample values (safe defaults)
    total_users = User.objects.count()
    total_admins = User.objects.filter(is_superuser=True).count()
    recent_users = User.objects.order_by("-date_joined")[:5]

    context = {
        "total_users": total_users,
        "total_admins": total_admins,
        "total_templates": 0,
        "total_ids": 0,
        "recent_users": recent_users,
    }

    return render(request, "idcard_app/admin_dashboard.html", context)


# =========================
# ADMIN PROFILE (VIEW + EDIT)
# =========================
@login_required
@admin_required
def admin_profile(request):

    if request.method == "POST":

        # edit name/email
        if "username" in request.POST:
            request.user.username = request.POST.get("username")
            request.user.email = request.POST.get("email")
            request.user.save()

        # change password
        if "new_password" in request.POST:
            np = request.POST.get("new_password")
            cp = request.POST.get("confirm_password")
            if np == cp:
                request.user.set_password(np)
                request.user.save()

        # upload photo (optional model)
        if "photo" in request.FILES:
            request.user.photo = request.FILES["photo"]
            request.user.save()

    return render(request,"idcard_app/admin_profile.html")


# =========================
# MANAGE USERS
# =========================
@login_required
@admin_required
def manage_users(request):

    users = (
        User.objects
        .exclude(is_superuser=True)
        .exclude(is_staff=True)
        .exclude(role__in=["admin", "employee", "staff"])
    )

    return render(
        request,
        "idcard_app/view_users.html",
        {"users": users}
    )


# =========================
# EDIT USER
# =========================
@login_required
@admin_required
def edit_user(request, user_id):

    user = get_object_or_404(User, id=user_id)
    
    # Get dashboard settings to control field visibility
    try:
        settings = DashboardSettings.objects.first()
    except:
        settings = None

    if request.method == "POST":
        # Basic Information
        user.username = request.POST.get("username", user.username)
        user.email = request.POST.get("email", user.email)
        user.first_name = request.POST.get("first_name", user.first_name)
        user.last_name = request.POST.get("last_name", user.last_name)
        
        # Personal Information
        user.role = request.POST.get("role", user.role)
        user.phone = request.POST.get("phone", "")
        user.emergency_mobile = request.POST.get("emergency_mobile", "")
        
        # Age/Date Information
        age = request.POST.get("age")
        if age:
            user.age = int(age)
        
        dob = request.POST.get("date_of_birth")
        if dob:
            user.date_of_birth = dob
            
        # Professional Information
        user.department = request.POST.get("department", "")
        user.roll_no = request.POST.get("roll_no", "")
        user.blood_group = request.POST.get("blood_group", "")
        user.address = request.POST.get("address", "")
        user.residence_status = request.POST.get("residence_status", "resident")
        
        # ID Card Information
        valid_upto = request.POST.get("valid_upto")
        if valid_upto:
            user.valid_upto = valid_upto
        
        # Photo Upload
        if "photo" in request.FILES:
            user.photo = request.FILES["photo"]
        
        # Signature Upload
        if "signature" in request.FILES:
            user.signature = request.FILES["signature"]
        
        # Password Change
        new_password = request.POST.get("new_password")
        if new_password and len(new_password) >= 8:
            user.set_password(new_password)
        
        user.save()
        messages.success(request, f"✓ User '{user.username}' updated successfully!")
        return redirect("manage_users")

    return render(request, "idcard_app/edit_form.html", {"user": user, "settings": settings})


# =========================
# TEMPLATE ADMIN PAGE
# =========================
@login_required
@admin_required
def template_admin(request, user_id=None):
    student = get_object_or_404(User, id=user_id) if user_id else request.user
    return render(request, "idcard_app/template_admin.html", {"student": student})


# =========================
# TEMPLATE DEBUG PAGE
# =========================
@login_required
@admin_required
def show_template_debug(request):
    return render(request, "idcard_app/template_debug.html")


@login_required
@admin_required
@require_POST
def save_design(request):
    try:
        payload = json.loads(request.body.decode('utf-8'))
    except Exception:
        return HttpResponseBadRequest('Invalid JSON')

    name = payload.get('name', 'Untitled')
    json_data = payload.get('json') or payload.get('data') or '{}'
    design_id = payload.get('id')

    if design_id:
        try:
            d = TemplateDesign.objects.get(id=design_id)
            d.name = name
            d.json_data = json.dumps(json_data)
            d.save()
        except TemplateDesign.DoesNotExist:
            return JsonResponse({'error': 'Design not found'}, status=404)
    else:
        d = TemplateDesign.objects.create(name=name, json_data=json.dumps(json_data), created_by=request.user)

    return JsonResponse({'ok': True, 'id': d.id, 'name': d.name})


@login_required
@admin_required
def list_designs(request):
    designs = TemplateDesign.objects.all().order_by('-updated_at')[:50]
    data = [{'id':d.id,'name':d.name,'updated_at':d.updated_at.isoformat()} for d in designs]
    return JsonResponse({'designs': data})


@login_required
@admin_required
def load_design(request, design_id):
    try:
        d = TemplateDesign.objects.get(id=design_id)
    except TemplateDesign.DoesNotExist:
        return JsonResponse({'error':'not found'}, status=404)
    # return stored JSON
    try:
        json_data = json.loads(d.json_data)
    except Exception:
        json_data = d.json_data
    return JsonResponse({'id': d.id, 'name': d.name, 'json': json_data})


@login_required
@admin_required
@require_POST
def batch_export(request):
    # Placeholder server-side API: accept list of users and design id, queue export job.
    try:
        payload = json.loads(request.body.decode('utf-8'))
    except Exception:
        return HttpResponseBadRequest('Invalid JSON')

    users = payload.get('users', [])
    design_id = payload.get('design_id')
    # In production, enqueue a background job to render each card server-side as PDF/PNG
    return JsonResponse({'ok': True, 'queued': len(users), 'note': 'Batch export queued (implement background renderer)'})


# =========================
# GENERATE ID CARD PAGE
# =========================
# GENERATE ID CARD PAGE
# =========================
@login_required
@admin_required
def generate_id_card(request):
    """Render generate ID card page with templates and users context"""
    try:
        # Get all templates
        templates = IDTemplate.objects.all().order_by('-id')
        templates_data = []
        for t in templates:
            try:
                template_json = t.template_json if isinstance(t.template_json, dict) else json.loads(str(t.template_json))
            except:
                template_json = {}
            templates_data.append({
                'id': t.id,
                'name': t.name,
                'json': template_json
            })
        
        # Get all users
        users = User.objects.all().values(
            'id', 'username', 'email', 'first_name', 'last_name',
            'role', 'department', 'phone', 'emergency_mobile', 'blood_group',
            'age', 'roll_no', 'photo', 'signature', 'address', 'residence_status',
            'date_of_birth', 'valid_upto'
        ).order_by('username')
        
        context = {
            'templates': templates_data,
            'users': list(users),
            'templates_json': json.dumps(templates_data),
            'users_json': json.dumps(list(users)),
        }
        return render(request, "idcard_app/generate_id.html", context)
    except Exception as e:
        import traceback
        traceback.print_exc()
        context = {
            'templates': [],
            'users': [],
            'templates_json': '[]',
            'users_json': '[]',
            'error': str(e)
        }
        return render(request, "idcard_app/generate_id.html", context)


# =========================
# DASHBOARD SETTINGS
# =========================
@login_required
@admin_required
def dashboard_settings(request):

    settings, created = DashboardSettings.objects.get_or_create(id=1)

    if request.method == "POST":
        settings.show_age = "show_age" in request.POST
        settings.show_department = "show_department" in request.POST
        settings.show_photo = "show_photo" in request.POST
        settings.show_phone = "show_phone" in request.POST
        settings.show_blood_group = "show_blood_group" in request.POST
        settings.show_roll_no = "show_roll_no" in request.POST
        settings.show_date_of_birth = "show_date_of_birth" in request.POST
        settings.show_emergency_mobile = "show_emergency_mobile" in request.POST
        settings.show_valid_upto = "show_valid_upto" in request.POST
        settings.show_signature = "show_signature" in request.POST
        settings.show_address = "show_address" in request.POST
        settings.show_role = "show_role" in request.POST
        settings.show_residence_status = "show_residence_status" in request.POST
        settings.save()
        messages.success(request, "✓ Settings updated successfully")
        return redirect("dashboard_settings")

    return render(
        request,
        "idcard_app/dashboard_settings.html",
        {"settings": settings}
    )


# =========================
# SIGNUP (BASIC USER)
# =========================
def signup_view(request):

    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        if password != confirm_password:
            messages.error(request, "Passwords do not match")
            return redirect("login")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return redirect("login")

        User.objects.create(
            username=username,
            password=make_password(password),
            role="user",
        )

        messages.success(request, "Account created successfully. Please login.")
        return redirect("login")

    return redirect("login")


# =========================
# FORGOT PASSWORD
# =========================
def forgot_password(request):
    if request.method == "POST":
        email = request.POST.get("email", "").strip().lower()
        new_password = request.POST.get("new_password", "")
        confirm_password = request.POST.get("confirm_password", "")

        if not email:
            messages.error(request, "Please enter your email address.")
            return redirect("forgot_password")

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            messages.error(request, "No account found with that email.")
            return redirect("forgot_password")

        if not new_password or not confirm_password:
            messages.error(request, "Please enter and confirm your new password.")
            return redirect("forgot_password")

        if new_password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect("forgot_password")

        if len(new_password) < 8:
            messages.error(request, "Password must be at least 8 characters long.")
            return redirect("forgot_password")

        user.set_password(new_password)
        user.save()
        messages.success(request, "Password updated successfully. You can now log in.")
        return redirect("login")

    return render(request, "idcard_app/forgot_password.html")



@csrf_exempt
def save_template(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=400)

    try:
        body = request.body.decode("utf-8")
        data = json.loads(body)

        name = data.get("name", "Untitled Template")
        template_json = data.get("template")

        obj = IDTemplate.objects.create(
            name=name,
            template_json=template_json
        )

        return JsonResponse({"status": "ok", "id": obj.id})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

from django.http import JsonResponse
from .models import SavedTemplate


def load_templates(request):
    templates = SavedTemplate.objects.all().order_by("-created_at")

    data = []
    for t in templates:
        data.append({
            "id": t.id,
            "name": t.name,
            "side": t.side,
            "data": t.data
        })

    return JsonResponse(data, safe=False)


# =========================
# API: GET ALL USERS (JSON)
# =========================
# API: GET ALL USERS (JSON)
# =========================
@csrf_exempt
def get_users_json(request):
    """Returns all users as JSON for template generation page"""
    try:
        users = User.objects.all().values(
            'id', 'username', 'email', 'first_name', 'last_name',
            'role', 'department', 'phone', 'emergency_mobile', 'blood_group',
            'age', 'roll_no', 'address', 'residence_status', 'date_of_birth',
            'valid_upto', 'photo', 'signature', 'is_staff', 'is_superuser'
        )
        users_list = list(users)
        
        return JsonResponse({
            'users': users_list,
            'status': 'ok',
            'count': len(users_list)
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({'error': str(e), 'status': 'error'}, status=500)


# =========================
# API: GET ALL ID TEMPLATES (JSON)
# =========================
@csrf_exempt
def get_id_templates(request):
    """Returns all saved ID templates for generation page"""
    try:
        templates = IDTemplate.objects.all().order_by('-id')
        
        data = []
        for t in templates:
            try:
                template_data = t.template_json if isinstance(t.template_json, dict) else json.loads(str(t.template_json))
            except:
                template_data = {}
            
            data.append({
                'id': t.id,
                'name': t.name,
                'json': template_data,
                'created_at': t.created_at.isoformat()
            })
        
        return JsonResponse({'templates': data, 'status': 'ok', 'count': len(data)})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({'error': str(e), 'status': 'error'}, status=500)


# =========================
# API: GET SINGLE ID TEMPLATE
# =========================
@csrf_exempt
def get_id_template_detail(request, template_id):
    """Returns single template for generation"""
    try:
        t = IDTemplate.objects.get(id=template_id)
        template_data = t.template_json if isinstance(t.template_json, dict) else json.loads(str(t.template_json))
        
        return JsonResponse({
            'id': t.id,
            'name': t.name,
            'json': template_data,
            'created_at': t.created_at.isoformat()
        })
    except IDTemplate.DoesNotExist:
        return JsonResponse({'error': 'Template not found'}, status=404)


@login_required
@admin_required
@require_POST
def delete_id_template(request, template_id):
    """Delete an ID template"""
    try:
        t = IDTemplate.objects.get(id=template_id)
        t.delete()
        return JsonResponse({'status': 'ok', 'deleted_id': template_id})
    except IDTemplate.DoesNotExist:
        return JsonResponse({'error': 'Template not found'}, status=404)


# =========================
# API: TEMPLATE DEBUG (Check saved templates)
# =========================
@login_required
def template_debug(request):
    """Debug endpoint to check saved templates"""
    try:
        templates = IDTemplate.objects.all()
        users = User.objects.all()
        
        debug_data = {
            'templates_count': templates.count(),
            'users_count': users.count(),
            'templates': [
                {
                    'id': t.id, 
                    'name': t.name,
                    'created_at': t.created_at.isoformat() if hasattr(t, 'created_at') else 'N/A'
                }
                for t in templates
            ],
            'users': [
                {
                    'id': u.id,
                    'username': u.username,
                    'email': u.email,
                    'role': u.role
                }
                for u in users
            ]
        }
        
        return JsonResponse(debug_data)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# =========================
# TEST API (No auth - for debugging fetch issues)
# =========================
def test_api(request):
    """Simple test endpoint without authentication"""
    return JsonResponse({
        'status': 'ok',
        'message': 'API is working',
        'user_authenticated': request.user.is_authenticated,
        'user': request.user.username if request.user.is_authenticated else 'Anonymous'
    })


# =========================
# BACKGROUND REMOVAL API
# =========================
from django.http import HttpResponse
import io

def remove_background_api(request, user_id):
    """Remove background from user's photo and return PNG with transparency"""
    try:
        from rembg import remove
        from PIL import Image
        
        user = get_object_or_404(User, id=user_id)
        
        if not user.photo:
            return JsonResponse({'error': 'No photo found'}, status=404)
        
        # Open the original photo
        input_image = Image.open(user.photo.path)
        
        # Remove background
        output_image = remove(input_image)
        
        # Save to bytes buffer as PNG (to preserve transparency)
        buffer = io.BytesIO()
        output_image.save(buffer, format='PNG')
        buffer.seek(0)
        
        # Return as PNG image
        return HttpResponse(buffer.getvalue(), content_type='image/png')
        
    except ImportError:
        return JsonResponse({'error': 'rembg not installed'}, status=500)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({'error': str(e)}, status=500)



