from pydantic import BaseModel, Field, root_validator, validator


class Url(BaseModel):
    base_url: str

    @validator('base_url')
    def check_base_url(cls, v):
        if not os.environ['BASE_URL'] in v:
            raise ValueError('error url')
        return v
