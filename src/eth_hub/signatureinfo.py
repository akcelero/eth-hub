from pydantic import UUID4, BaseModel, Field, NonNegativeInt


class SignatureInfo(BaseModel):
    key_id: UUID4
    hash: bytes
    v: NonNegativeInt = Field(..., ge=0, le=1)
    r: NonNegativeInt = Field(
        ...,
        examples=[
            "70104486010083990545032612337028745446547141775874126017519489994121216695741"
        ],
    )
    s: NonNegativeInt = Field(
        ...,
        examples=[
            "43255222980758551805236299871263068442915545698769795282667456674396607541627"
        ],
    )
