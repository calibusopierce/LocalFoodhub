from django.urls import include, path

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('home.html', views.home, name='home'),
    path('login.html', views.log_in, name='log_in'),
    path('register.html', views.register, name='register'),
    path('about.html', views.about, name='about'),
    path('orders.html', views.orders, name='orders'),
    path('cart.html', views.cart, name='cart'),
    path('checkout.html', views.checkout, name='checkout'),
    path('menu.html', views.menu, name='menu'),
    path('download-excel', views.download_excel, name='download_excel'),
    path('menu-<stall_name>.html', views.filtered_menu, name='filtered_menu'),
    path('contact.html', views.contact, name='contact'),
    path('search.html', views.search, name='search'),
    path('profile.html', views.profile, name='profile'),
    path('update_profile.html', views.update_profile, name='update_profile'),
    path('add_product.html', views.add_product, name='add_product'),
    path('update_address.html', views.update_address, name='update_address'),
    path('dashboard.html', views.dashboard, name='dashboard'),

    path('report_generator', views.report_generator, name='report_generator'),

    path('chart.html', views.chart, name='chart'),
    path('calendar.html', views.calendar, name='calendar'),
    path('user_logout',views.user_logout,name='user_logout'),
    path('change_password.html', views.change_password, name='change_password'),
]


