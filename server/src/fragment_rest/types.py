from pydantic import BaseModel


class FragmentAPIObject(BaseModel):
    pass


class FragmentAPIResponseObject(FragmentAPIObject):
    ok: bool


class FragmentFoundRecipientData(FragmentAPIObject):
    myself: bool
    recipient: str
    photo: str
    name: str


class FragmentRecipientData(FragmentAPIResponseObject):
    found: FragmentFoundRecipientData
