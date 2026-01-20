from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from .models import CustomUser, OtpToken, Product, ProductImage, ProductVariation, Category
from django import forms

class CustomUserCreationForm(forms.ModelForm):
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = CustomUser
        fields = ('username', 'email')

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_superuser', 'is_active', 'account_status', 'created_date')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'is_oauth_pending', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('-date_joined',)
    
    fieldsets = (
        ('Account Information', {
            'fields': ('username', 'email', 'password')
        }),
        ('Personal Info', {
            'fields': ('first_name', 'last_name', 'avatar', 'contact', 'address')
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
            'classes': ('collapse',)
        }),
        ('OAuth & Account Status', {
            'fields': ('is_oauth_pending', 'botpress_user_key'),
            'classes': ('collapse',)
        }),
        ('Important Dates', {
            'fields': ('last_login', 'date_joined'),
            'classes': ('collapse',)
        }),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'is_staff', 'is_superuser')
        }),
    )
    
    readonly_fields = ('last_login', 'date_joined')
    
    def account_status(self, obj):
        """Display colored account status"""
        if not obj.is_active:
            color = '#d9534f'
            status = 'Inactive'
        elif obj.is_oauth_pending:
            color = '#f0ad4e'
            status = 'OAuth Pending'
        elif obj.is_superuser:
            color = '#5cb85c'
            status = 'Admin'
        elif obj.is_staff:
            color = '#5bc0de'
            status = 'Staff'
        else:
            color = '#5cb85c'
            status = 'Active'
        
        return format_html(
            '<span style="color: white; background-color: {}; padding: 5px 10px; border-radius: 4px;">{}</span>',
            color,
            status
        )
    account_status.short_description = 'Account Status'
    
    def created_date(self, obj):
        """Display formatted created date"""
        return obj.date_joined.strftime('%Y-%m-%d %H:%M')
    created_date.short_description = 'Created'
    
    actions = ['make_active', 'make_inactive', 'make_staff', 'remove_staff', 'make_admin', 'remove_admin']
    
    def make_active(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} user(s) activated.')
    make_active.short_description = 'Activate selected users'
    
    def make_inactive(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} user(s) deactivated.')
    make_inactive.short_description = 'Deactivate selected users'
    
    def make_staff(self, request, queryset):
        updated = queryset.update(is_staff=True)
        self.message_user(request, f'{updated} user(s) promoted to staff.')
    make_staff.short_description = 'Promote to Staff'
    
    def remove_staff(self, request, queryset):
        updated = queryset.update(is_staff=False, is_superuser=False)
        self.message_user(request, f'{updated} user(s) removed from staff.')
    remove_staff.short_description = 'Remove Staff status'
    
    def make_admin(self, request, queryset):
        updated = queryset.update(is_superuser=True, is_staff=True)
        self.message_user(request, f'{updated} user(s) promoted to admin.')
    make_admin.short_description = 'Promote to Admin'
    
    def remove_admin(self, request, queryset):
        updated = queryset.update(is_superuser=False, is_staff=False)
        self.message_user(request, f'{updated} user(s) removed from admin.')
    remove_admin.short_description = 'Remove Admin status'

@admin.register(OtpToken)
class OtpTokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'otp_code', 'is_expired', 'created_time', 'expires_time', 'last_resend')
    list_filter = ('tp_created_at', 'otp_expires_at')
    search_fields = ('user__username', 'user__email', 'otp_code')
    readonly_fields = ('user', 'otp_code', 'tp_created_at', 'otp_expires_at', 'last_resend_at')
    ordering = ('-tp_created_at',)
    
    def is_expired(self, obj):
        """Display if OTP is expired"""
        from django.utils import timezone
        if obj.otp_expires_at < timezone.now():
            return format_html('<span style="color: #d9534f; font-weight: bold;">Expired</span>')
        return format_html('<span style="color: #5cb85c; font-weight: bold;">Active</span>')
    is_expired.short_description = 'Status'
    
    def created_time(self, obj):
        return obj.tp_created_at.strftime('%Y-%m-%d %H:%M:%S')
    created_time.short_description = 'Created At'
    
    def expires_time(self, obj):
        return obj.otp_expires_at.strftime('%Y-%m-%d %H:%M:%S') if obj.otp_expires_at else 'N/A'
    expires_time.short_description = 'Expires At'
    
    def last_resend(self, obj):
        if obj.last_resend_at:
            return obj.last_resend_at.strftime('%Y-%m-%d %H:%M:%S')
        return 'Never'
    last_resend.short_description = 'Last Resend'
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1

class ProductVariationInline(admin.TabularInline):
    model = ProductVariation
    extra = 1
    fields = ('product_variation', 'description', 'price', 'stock', 'image')
    list_display = ('product_variation', 'price', 'stock')

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'brand', 'category_name', 'price', 'has_3d_model', 'variant_count')
    fieldsets = (
        ('Basic Information', {
            'fields': ('product_name', 'description', 'brand', 'category_name')
        }),
        ('Pricing & Stock', {
            'fields': ('price', 'stock')
        }),
        ('Images & Media', {
            'fields': ('image', 'model_3d')
        }),
    )
    inlines = [ProductImageInline, ProductVariationInline]
    actions = ['add_variant_action']
    
    def has_3d_model(self, obj):
        return bool(obj.model_3d)
    has_3d_model.boolean = True
    has_3d_model.short_description = 'Has 3D Model'
    
    def variant_count(self, obj):
        return obj.variations.count()
    variant_count.short_description = 'Variants'
    
    def add_variant_action(self, request, queryset):
        """Action to add variant to selected products"""
        for product in queryset:
            ProductVariation.objects.get_or_create(
                product=product,
                product_variation='New Variant',
                defaults={
                    'price': product.price,
                    'stock': product.stock,
                }
            )
        self.message_user(request, f'Variant creation initiated for {queryset.count()} product(s). Please edit them to customize.')
    add_variant_action.short_description = 'Add new variant to selected products'