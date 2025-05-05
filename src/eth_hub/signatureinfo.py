from pydantic import BaseModel, UUID4, PositiveInt, Field


class SignatureInfo(BaseModel):
    key_id: UUID4
    hash: bytes
    v: PositiveInt = Field(..., ge=27, examples=[27])
    r: str = Field(
        ...,
        max_length=66,
        min_length=66,
        json_schema_extra={"format": "hexadecimal"},
        examples=[f"0x{0:0>64}"],
    )
    s: str = Field(
        ...,
        max_length=66,
        min_length=66,
        json_schema_extra={"format": "hexadecimal"},
        examples=[f"0x{0:0>64}"],
    )
