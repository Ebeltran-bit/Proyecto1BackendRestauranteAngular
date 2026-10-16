from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator

# Upper limit that catches typing mistakes (for example 100 instead of 10).
MAX_QUANTITY = 99
MAX_NOTES_LENGTH = 200


class Order(BaseModel):
    """Line of an order: one product, in one presentation, for one table."""

    id: int
    table_id: int
    product_id: int
    presentation_id: int
    quantity: int
    unit_price: float
    notes: Optional[str] = None


class OrderCreate(BaseModel):
    """JSON body to add an order to a table. The table comes from the URL."""

    # strict: "2" is not accepted as 2; extra="forbid": unknown fields are rejected.
    model_config = ConfigDict(strict=True, extra="forbid", str_strip_whitespace=True)

    product_id: int = Field(gt=0)
    presentation_id: int = Field(gt=0)
    quantity: int = Field(ge=1, le=MAX_QUANTITY)
    notes: Optional[str] = Field(default=None, max_length=MAX_NOTES_LENGTH)


class OrderUpdate(BaseModel):
    """JSON body to change an order. Only the fields sent are modified."""

    model_config = ConfigDict(strict=True, extra="forbid", str_strip_whitespace=True)

    presentation_id: Optional[int] = Field(default=None, gt=0)
    quantity: Optional[int] = Field(default=None, ge=1, le=MAX_QUANTITY)
    # Sending "notes": null (or an empty text) removes the notes.
    notes: Optional[str] = Field(default=None, max_length=MAX_NOTES_LENGTH)

    @model_validator(mode="after")
    def check_fields(self) -> "OrderUpdate":
        if not self.model_fields_set:
            raise ValueError("Indica al menos un campo a modificar: presentation_id, quantity o notes")
        for field in self.model_fields_set - {"notes"}:
            if getattr(self, field) is None:
                raise ValueError(f"El campo {field} no puede ser null")
        return self
