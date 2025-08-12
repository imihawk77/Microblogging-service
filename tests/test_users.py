from http import HTTPStatus

from httpx import AsyncClient

from tests.good_responses import get_result, get_user


async def test_users_me(ac: AsyncClient):
    """
    Тест получения данных текущего пользователя
    """
    response = await ac.get("/api/users/me", headers={"api-key": "test_1"})
    user_data = response.json()
    assert response.status_code == HTTPStatus.OK
    assert user_data == get_user


async def test_user_by_id(ac: AsyncClient) -> None:
    """
    Тест получения данных пользователя id == 1
    """
    response = await ac.get("/api/users/1")
    user_data = response.json()
    assert response.status_code == HTTPStatus.OK
    assert user_data == get_user


async def test_add_follow(ac: AsyncClient) -> None:
    """
    Тест добавления подписчика
    """
    response = await ac.post(
        "/api/users/1/follow", headers={"api-key": "test_1"}
    )
    add_follow_data = response.json()
    assert response.status_code == HTTPStatus.OK
    assert add_follow_data == get_result


async def test_delete_follow(ac: AsyncClient) -> None:
    """
    Тест удаления подписчика
    """
    response = await ac.delete(
        "/api/users/1/follow", headers={"api-key": "test_2"}
    )
    del_follow_data = response.json()
    assert response.status_code == HTTPStatus.OK
    assert del_follow_data == get_result
