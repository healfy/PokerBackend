import random
from fastapi import Depends, APIRouter, Response, status
from .dependencies import check_access, get_lobby_service, set_cookie, get_user_id
from backend.apps.lobby.service import LobbyService
from backend.apps.lobby.schema import TableSchema
from backend.apps.lobby.consts import SeatStatus
from ...apps.lobby.errors import LobbyError

router = APIRouter(prefix="/tables", dependencies=[Depends(check_access), Depends(set_cookie)])

names = ['Mexico', 'Minsk', 'Amsterdam']


@router.post('/')
async def create_table(
        service: LobbyService = Depends(get_lobby_service)
) -> Response:
    await service.create_table(f'{random.choice(names)}_{random.randint(1, 1000000)}')
    return Response()


@router.get('/{table_id}')
async def get_table(
        table_id: int,
        service: LobbyService = Depends(get_lobby_service),
        user_id: int = Depends(get_user_id),
) -> TableSchema:
    data = await service.get_table(table_id)
    data = TableSchema.from_orm(data)
    data.user_here = user_id in set(seat.user.id for seat in data.seats if seat.user)
    data.available = len([s for s in data.seats if s.status == SeatStatus.FREE]) > 0
    return data


@router.put("/{table_id}")
async def take_a_seat(
        table_id: int,
        service: LobbyService = Depends(get_lobby_service),
        user_id: int = Depends(get_user_id)
):
    try:
        await service.reserve_seat(table_id, user_id)
    except LobbyError as exc:
        return Response(status_code=status.HTTP_400_BAD_REQUEST, content={"data": exc.message})
    return Response(status_code=status.HTTP_200_OK)
