from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import F
from .models import Bd, Rubric
from .forms import BdForm, OrderForm
import requests


if __name__ == '__main__':
    from django.db.models import F


# 1. Головна сторінка
def index(request):
    bbs = Bd.objects.all()
    rubrics = Rubric.objects.all()
    return render(request, 'samples/index.html', {
        'bbs': bbs,
        'rubrics': rubrics
    })


# 2. Сторінка товарів за рубриками
def by_rubric(request, rubric_id):
    bbs = Bd.objects.filter(rubric=rubric_id)
    rubrics = Rubric.objects.all()
    current_rubric = get_object_or_404(Rubric, pk=rubric_id)
    return render(request, 'samples/by_rubric.html', {
        'bbs': bbs,
        'rubrics': rubrics,
        'current_rubric': current_rubric
    })


# 3. Додавання нового оголошення
def add_and_save(request):
    if request.method == 'POST':
        form = BdForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('index')
    else:
        form = BdForm()
    rubrics = Rubric.objects.all()
    return render(request, 'samples/add.html', {'form': form, 'rubrics': rubrics})


def add_to_cart(request, pk):
    product = get_object_or_404(Bd, pk=pk)
    cart = request.session.get('cart', {})

    # БЕЗПЕКА: Якщо в сесії старий список [] замість словника {}, чистимо його
    if not isinstance(cart, dict):
        cart = {}

    product_id = str(pk)

    if product.stock > 0:
        current_qty = cart.get(product_id, 0)
        if current_qty < product.stock:
            cart[product_id] = current_qty + 1

        request.session['cart'] = cart
        request.session.modified = True

    return redirect(request.META.get('HTTP_REFERER', 'index'))

# 5. Сторінка кошика (ВИПРАВЛЕНО)
def show_cart(request):
    cart = request.session.get('cart', {})
    # Дістаємо об'єкти товарів за ключами словника
    products = Bd.objects.filter(pk__in=cart.keys())

    cart_items = []
    total_price = 0

    for product in products:
        quantity = cart[str(product.pk)]
        subtotal = product.price * quantity
        total_price += subtotal
        cart_items.append({
            'product': product,
            'quantity': quantity,
            'subtotal': subtotal
        })

    rubrics = Rubric.objects.all()
    return render(request, 'samples/cart.html', {
        'cart_items': cart_items,
        'total_price': total_price,
        'rubrics': rubrics
    })


# 6. Очищення кошика
def clear_cart(request):
    if 'cart' in request.session:
        del request.session['cart']
        request.session.modified = True
    return redirect('cart')


def checkout(request):
    cart = request.session.get('cart', {})
    if not cart:
        return redirect('index')

    products = Bd.objects.filter(pk__in=cart.keys())
    total_price = 0
    items_list = []

    # Готуємо дані для замовлення
    for p in products:
        qty = cart.get(str(p.pk), 0)
        total_price += p.price * qty
        items_list.append(f"{p.title} ({qty} шт.)")

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            # 1. Віднімаємо кількість зі складу (БЕЗПЕЧНО)
            for p in products:
                qty = cart.get(str(p.pk), 0)
                if p.stock >= qty:
                    Bd.objects.filter(pk=p.pk).update(stock=F('stock') - qty)
                else:
                    Bd.objects.filter(pk=p.pk).update(stock=0)

            # 2. Зберігаємо замовлення
            order = form.save(commit=False)
            order.items = ", ".join(items_list)
            order.total_price = total_price
            order.save()

            # --- ТЕЛЕГРАМ-СПОВІЩЕННЯ ---
            telegram_text = (
                f"🚀 НОВЕ ЗАМОВЛЕННЯ №{order.pk}!\n\n"
                f"👤 Клієнт: {form.cleaned_data.get('last_name')} {form.cleaned_data.get('first_name')}\n"
                f"📞 Телефон: {form.cleaned_data.get('phone')}\n"
                f"📧 Email: {form.cleaned_data.get('email')}\n\n"
                f"📍 Доставка: {form.cleaned_data.get('region')} обл., м. {form.cleaned_data.get('city')}\n"
                f"🏢 Служба: {form.cleaned_data.get('delivery_service')} ({form.cleaned_data.get('delivery_type')})\n"
                f"📦 Відділення: {form.cleaned_data.get('department')}\n\n"
                f"🛍 Товари: {order.items}\n"
                f"💰 Сума: {order.total_price} грн."
            )

            send_telegram_message(telegram_text)

            # 3. Очищення кошика
            request.session['cart'] = {}
            request.session.modified = True
            return render(request, 'samples/success.html', {'order': order})
    else:
        form = OrderForm()

    return render(request, 'samples/checkout.html', {
        'form': form,
        'total_price': total_price,
        'cart_items': products
    })
# 8. Запит постачальнику
def order_request(request, pk):
    product = get_object_or_404(Bd, pk=pk)
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            qty = request.POST.get('quantity', 1)
            order.items = f"ЗАПИТ ПОСТАЧАЛЬНИКУ: {product.title} ({qty} шт.)"
            order.total_price = product.price * int(qty)
            order.save()

            # --- ДОДАЙ ЦЕЙ БЛОК СЮДИ ---
            telegram_text = f"☎️ ЗАПИТ ПОСТАЧАЛЬНИКУ!\nТовар: {product.title}\nКількість: {qty}\nСума: {order.total_price} грн."
            send_telegram_message(telegram_text)
            # ---------------------------

            return render(request, 'samples/success.html', {'order': order})
    else:
        form = OrderForm()
    return render(request, 'samples/order_request_form.html', {'product': product, 'form': form})

def cart_total(request):
    cart = request.session.get('cart', {})
    total = 0
    if isinstance(cart, dict):
        total = sum(cart.values())
    return {'cart_total_quantity': total}


def remove_from_cart(request, pk):
    cart = request.session.get('cart', {})
    product_id = str(pk)

    if product_id in cart:
        del cart[product_id]  # Видаляємо саме цей товар
        request.session['cart'] = cart
        request.session.modified = True

    return redirect('cart')  # Повертаємо користувача назад у кошик


def send_telegram_message(message):
    # 1. Твій токен бота (той самий, що був раніше)
    token = "8003871381:AAHJNp2gl-yTsuBCHHgQdWF50bZfGZ7mtAo"

    # 2. СПИСОК ОТРИМУВАЧІВ у квадратних дужках []
    # Перше число — твій ID (6993601297).
    # Друге число — ID твоєї сестри (Юлі).
    # ЗАМІНИ "0000000000" на її справжнє ID, коли побачиш його в терміналі.
    recipients = ["6993601297", "123456789"]

    for chat_id in recipients:
        # 3. URL для кожного отримувача
        url = f"https://api.telegram.org/bot{token}/sendMessage"

        # 4. ТЕКСТ РЕКЛАМИ для Юлі
        # Ти можеш змінити цей текст на будь-який інший
        promo_text = (
            "📅 **DOLCE STORE: НОВИНКА!**\n\n"
            "Привіт! У нас з'явилися круті календарі на 2026 рік. 🎁\n"
            "Замовляй прямо зараз за спеціальною ціною:\n"
            "http://127.0.0.1:8000/"
        )

        # 5. Дані для відправки
        data = {
            "chat_id": chat_id,
            "text": promo_text,
            "parse_mode": "Markdown"  # Робить текст жирним і красивим
        }

        try:
            # 6. Відправка повідомлення (круглі дужки для функції)
            response = requests.post(url, data=data, timeout=5)

            # Вивід у термінал PyCharm для контролю
            print(f"Відправлено на ID {chat_id}, статус: {response.status_code}")

        except Exception as e:
            print(f"Помилка при відправці на {chat_id}: {e}")