import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
from shoes_market import settings


class EmailService:
    def __init__(self, api_key: str, from_email: str, from_name: str):
        configuration = sib_api_v3_sdk.Configuration()
        configuration.api_key["api-key"] = api_key

        self.api = sib_api_v3_sdk.TransactionalEmailsApi(
            sib_api_v3_sdk.ApiClient(configuration)
        )
        self.from_email = from_email
        self.from_name = from_name

    async def send_email(self, to_email: str, subject: str, html: str) -> None:
        email = sib_api_v3_sdk.SendSmtpEmail(
            sender={
                "name": self.from_name,
                "email": self.from_email,
            },
            to=[
                {
                    "email": to_email,
                }
            ],
            subject=subject,
            html_content=html,
        )

        try:
            self.api.send_transac_email(email)
        except ApiException as e:
            raise RuntimeError(f"Ошибка отправки письма: {e}")


email_service = EmailService(
    api_key=settings.BREVO_API_KEY,
    from_email=settings.MAIL_FROM,
    from_name=settings.MAIL_FROM_NAME,
)
