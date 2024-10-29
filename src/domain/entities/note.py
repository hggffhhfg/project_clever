from dataclasses import dataclass
from functools import total_ordering
from operator import eq, gt
from typing import TYPE_CHECKING
from typing_extensions import Self
from uuid import UUID

from src.domain.entities import BaseEntity, IDurations, IStatistics


if TYPE_CHECKING:
    from src.domain.values.points import Points


@total_ordering
@dataclass(eq=False, kw_only=True)
class NoteEntity(BaseEntity):
    owner_oid: UUID
    points: "Points"
    durations: IDurations | None = None
    statistics_of_points: IStatistics | None = None

    def __eq__(self: Self, other: object) -> bool:
        if not isinstance(other, NoteEntity):
            return NotImplemented
        return eq(
            (self.points.bedtime_date, self.owner_oid),
            (other.points.bedtime_date, other.owner_oid),
        )

    def __hash__(self: Self) -> int:
        return hash((self.points.bedtime_date, self.owner_oid))

    def __gt__(self: Self, other: object) -> bool:
        if not isinstance(other, NoteEntity):
            return NotImplemented
        return gt(self.points.bedtime_date, other.points.bedtime_date)
