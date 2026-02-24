from fastapi import APIRouter
from app.api.endpoints import tag, users, auth, cart, checkout, google_auth, orders, otp, products, wishlist, recentview

api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(products.router)
api_router.include_router(cart.router)
api_router.include_router(wishlist.router)
api_router.include_router(otp.router)
api_router.include_router(checkout.router)
api_router.include_router(orders.router)
api_router.include_router(google_auth.router)
api_router.include_router(recentview.router)
api_router.include_router(tag.router)