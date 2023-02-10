from django import template
register = template.Library()

from .. models import AddedToCart

@register.simple_tag
def subTotalCalculator(product_price, quantity):
    sub_total = int(product_price) * int(quantity)

    return sub_total

@register.simple_tag
def cartTotal(my_cart):

    cart_total = 0

    for my_cart in my_cart:
        quantity = int(my_cart.quantity)
        product_price = int(my_cart.product.product_price)
        total = quantity * product_price

        cart_total = cart_total + total

    return cart_total

@register.simple_tag
def count_pending_orders(customer):
    added_to_cart = AddedToCart.objects.filter(customer = customer, is_pending = True).all()

    return len(added_to_cart) #3


@register.simple_tag
def report_generator_get_total(orders_list):

    i = 0
    for order in orders_list:
        i = i + (order.product.product_price * order.quantity)

    return i


@register.simple_tag
def get_items_of_my_order(my_orders):
    added_to_cart = AddedToCart.objects.filter(order_id = my_orders.order_id).all()

    i = 0

    for cart in added_to_cart:
        i = i + cart.total_of_items

    return added_to_cart, i 