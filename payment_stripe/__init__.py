import stripe
from payment_stripe import settings

stripe.api_key = settings.STRIPE_SECRET_KEY