from http import HTTPStatus
from typing import List, Optional

import loguru
from pydantic import BaseModel, ConfigDict, Field, field_validator
from starlette.exceptions import HTTPException

from src.core.config import LENGTH_TWEET
from src.core.schemas.schema_base import ResponseSchema
from src.core.schemas.schema_image import ImagePathSchema

from src.core.schemas.schema_likes import LikeSchema
from src.core.schemas.schema_users import BaseUserSchema


class TweetOutSchema(BaseModel):
    """
    Схема для вывода твита, автора, вложенных изображений и данных по лайкам
    """

    id: int
    tweet_text: str = Field(
        alias="content",
        default="Хоп Хей Ла Лей.",
    )
    user: BaseUserSchema = Field(alias="author")
    likes: List[LikeSchema]
    images: List[str] = Field(alias="attachments")

    @field_validator("images", mode="before")
    def serialize_images(cls, img_values: List[ImagePathSchema]):
        """
        Возвращаем список строк, ссылкой на изображение
        """
        if isinstance(img_values, list):
            return [img_value.path_media for img_value in img_values]
        loguru.logger.debug(
            f"Путь к картинке ----------------------------> {img_values}"
        )
        return img_values

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,  # Использовать псевдоним вместо названия поля
    )


class TweetInSchema(BaseModel):
    """
    Схема для входных данных при добавлении нового твита
    """

    tweet_data: str = Field()
    tweet_media_ids: Optional[list[int]]

    @field_validator("tweet_data", mode="before")
    def check_len_tweet_data(cls, tweet_message: str) -> str | None:
        """
        Проверка длины твита
        """
        if len(tweet_message) > LENGTH_TWEET:
            raise HTTPException(
                status_code=HTTPStatus.UNPROCESSABLE_ENTITY,  # 422
                detail=f"Сообщение не может быть длиннее 280 символов."
                f"Длина сообщения: {len(tweet_message)} символов.",
            )

        return tweet_message

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,  # Использовать псевдоним вместо названия поля
    )


class TweetListSchema(BaseModel):
    """
    Схема для вывода списка твитов
    """

    tweets: List[TweetOutSchema]


class TweetResponseSchema(ResponseSchema):
    """
    Схема для вывода id твита после публикации
    """

    id: int = Field(alias="tweet_id")
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,  # Использовать псевдоним вместо названия поля
    )