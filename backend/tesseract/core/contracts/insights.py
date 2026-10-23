from datetime import date
from typing import Literal, Self

from pydantic import model_validator

from .common import ArtifactRef, Contract, Count, DerivedRecord, Instant, NonNegative, Text, ordered


class Share(Contract):
    """``count`` of ``of``: a part always carries the denominator it was counted against."""

    key: Text
    count: Count
    of: Count

    @model_validator(mode="after")
    def part_of_whole(self) -> Self:
        if self.count > self.of:
            raise ValueError("a share cannot exceed its denominator")
        return self


def _breakdown(shares: tuple[Share, ...], total: int, name: str) -> None:
    if any(s.of != total for s in shares) or sum(s.count for s in shares) != total:
        raise ValueError(f"{name} must split exactly its denominator")
    if len({s.key for s in shares}) != len(shares):
        raise ValueError(f"{name} keys must be unique")


class ProductInsight(DerivedRecord):
    """Sales, POS returns and reported reasons of one product over one perimeter and period.

    Every count is over the same ``stores`` and the same local business days
    ``period_first..period_last``. Reported reasons are shares of counted observations, never of
    sales: there is no conversion rate without a denominator of shoppers.
    """

    as_of: Instant
    level: Literal["sku", "style"]
    product_id: Text
    stores: tuple[Text, ...]
    period_first: date
    period_last: date
    units_sold: Count
    units_returned: Count
    return_rate: NonNegative | None
    return_lines: Count
    return_reasons: tuple[Share, ...]
    n_observations: Count
    n_documents: Count
    reported_kinds: tuple[Share, ...]
    reported_reasons: tuple[Share, ...]
    observation_refs: tuple[ArtifactRef, ...]
    notes: tuple[str, ...] = ()

    @model_validator(mode="after")
    def consistent_denominators(self) -> Self:
        ordered(self.period_first, self.period_last)
        if not self.stores:
            raise ValueError("an insight needs its store perimeter")
        expected = self.units_returned / self.units_sold if self.units_sold else None
        if self.return_rate != expected:
            raise ValueError("return_rate must be units_returned / units_sold, or None if no sale")
        _breakdown(self.return_reasons, self.return_lines, "return_reasons")
        _breakdown(self.reported_kinds, self.n_observations, "reported_kinds")
        _breakdown(self.reported_reasons, self.n_observations, "reported_reasons")
        if len(self.observation_refs) != self.n_observations:
            raise ValueError("n_observations must count observation_refs")
        if self.n_documents > self.n_observations:
            raise ValueError("documents cannot outnumber the observations they hold")
        return self
