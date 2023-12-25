from typing import Iterable, Any
import stripe


def get_item(items: Iterable[Any]) -> list:
    """Возвращает список price_id для корзины Order"""
    list_price_id = []
    for item in items:
        price = stripe.Price.create(
            currency=item.currency,
            unit_amount=item.price,
            product_data={"name": item.name},
        )
        data_price = {
            'price': price.id,
            'quantity': 1,
        }
        # # Если есть налог, добавляем его
        if item.tax.percentage:
            data_price['tax_rates'] = [item.tax.tax_id]
        list_price_id.append(data_price)

    return list_price_id