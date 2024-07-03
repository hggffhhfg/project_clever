import abc

from datetime import (
    date,
    time,
    timedelta,
)
from typing import (
    Annotated,
    ClassVar,
)
from typing_extensions import Self

from pydantic import (
    AfterValidator,
    BaseModel,
    ConfigDict,
    Field,
    computed_field,
)

from src.domain.note import utils


StrToTime = Annotated[time | str, AfterValidator(utils.normalize_str_to_time)]
StrToDate = Annotated[date | str, AfterValidator(utils.normalize_str_to_date)]


class NoteValueObjectBase(BaseModel, abc.ABC):
    bedtime_date: StrToDate = Field(
        title="Дата отхода ко сну",
        description="",
        examples=["2020-12-12", "2021-01-20"],
    )
    went_to_bed: StrToTime = Field(
        title="Время отхода ко сну",
        description="",
        examples=["01:00", "13:00"],
    )
    fell_asleep: StrToTime = Field(
        title="Время засыпания",
        description="",
        examples=["03:00", "15:00"],
    )
    woke_up: StrToTime = Field(
        title="Время пробуждения",
        description="",
        examples=["11:00", "23:00"],
    )
    got_up: StrToTime = Field(
        title="Время подъема",
        description="",
        examples=["13:00", "01:00"],
    )
    no_sleep: StrToTime = Field(
        default=time(hour=0, minute=0),
        title="Время отсутствия сна (в ЧЧ:ММ)",
        description="",
        examples=["00:00", "00:20"],
    )
    model_config: ClassVar[ConfigDict] = ConfigDict(
        frozen=True,
        extra="forbid",
    )

    def __eq__(self: Self, other: object) -> bool:
        if not isinstance(other, NoteValueObjectBase):
            return NotImplemented
        return self.bedtime_date == other.bedtime_date

    def __hash__(self: Self) -> int:
        return hash(self.bedtime_date)


class NoteDurationsBase(abc.ABC):
    @computed_field(  # type: ignore[misc]
        title="Длительность сна без учета времени отсутствия сна",
        return_type=timedelta,
    )
    @property
    @abc.abstractmethod
    def _sleep_duration_without_no_sleep(self: Self) -> timedelta: ...

    @computed_field(  # type: ignore[misc]
        title="Длительность времени, проведенного в постели.",
        return_type=timedelta,
    )
    @property
    @abc.abstractmethod
    def _in_bed_duration(self: Self) -> timedelta: ...

    @computed_field(  # type: ignore[misc]
        title="Длительность отсутствия сна (секунд)",
        return_type=timedelta,
    )
    @property
    @abc.abstractmethod
    def _no_sleep_duration(self: Self) -> timedelta: ...


class NoteStatisticBase(abc.ABC):
    @computed_field(
        title="",
        return_type=time,
    )
    @property
    @abc.abstractmethod
    def time_in_sleep(self) -> time: ...

    @computed_field(
        title="",
        return_type=time,
    )
    @property
    @abc.abstractmethod
    def time_in_bed(self) -> time: ...

    @computed_field(
        title="",
        return_type=float,
    )
    @property
    @abc.abstractmethod
    def sleep_efficiency(self) -> float: ...


class NoteBase(
    NoteValueObjectBase,
    NoteDurationsBase,
    NoteStatisticBase,
    abc.ABC,
):
    ...  # fmt: skip
