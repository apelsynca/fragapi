from pytonapi.rest import TonapiRestClient

from src.config import settings

rest_client = TonapiRestClient(api_key=settings.TONAPI_API_KEY)
