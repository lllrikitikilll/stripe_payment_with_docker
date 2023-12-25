FROM python:3.10

RUN mkdir -p usr/src/app
COPY . usr/src/app
WORKDIR usr/src/app

# Установка библиотек, создание и применение миграций
RUN pip install --no-cache-dir -r requirements.txt
RUN python manage.py makemigrations
RUN python manage.py migrate


# Создание суперпользователя
RUN echo "from django.contrib.auth.models import User; \
     User.objects.create_superuser('root', 'admin@example.com', 'root')" | python manage.py shell

# Создание базовых данных в таблице Discount и Tax
RUN echo "from payment_app.models import Discount, Tax; \
    tax = Tax(display_name='Без налога', percentage=0); \
    dis = Discount(name='Без скидки', percent_off='0'); \
    tax.save(); \
    dis.save()" | python manage.py shell

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
