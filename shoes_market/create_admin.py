import asyncio
import os

from sqlalchemy import select

from shoes_market.database import async_session
from shoes_market.users import models
from shoes_market.orders import models as prod_models
from shoes_market.products import models as orders_models
from shoes_market.utils import hash_password


async def main():
    email = os.getenv("ADMIN_EMAIL")
    password = os.getenv("ADMIN_PASSWORD")
    phone_number = os.getenv("ADMIN_PHONE", "+77770000000")

    if not email or not password:
        print("ADMIN_EMAIL or ADMIN_PASSWORD is not set")
        return

    async with async_session() as session:
        result = await session.execute(
            select(models.User).where(models.User.email == email)
        )
        user = result.scalar_one_or_none()

        if user:
            print(f"Admin already exists: {email}")
            return

        admin = models.User(
            nickname="admin",
            phone_number=phone_number,
            email=email,
            password=hash_password(password),
            image=None,
            first_name="Admin",
            last_name="User",
            gender=None,
            birth_date=None,
            telegram_id=None,
            is_staff=True,
            is_active=True,
            last_login=None,
        )

        session.add(admin)
        await session.commit()

        print(f"Admin created: {email}")


if __name__ == "__main__":
    asyncio.run(main())