from fastapi import FastAPI
from app.router import users, auth, products, cart, wishlist, otp, checkout
from app.database import engine, Base

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(products.router)
app.include_router(cart.router)
app.include_router(wishlist.router)
app.include_router(otp.router)
app.include_router(checkout.router)