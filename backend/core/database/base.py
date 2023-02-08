from sqlalchemy import BigInteger, Column, MetaData
from sqlalchemy.orm import declarative_base


metadata = MetaData(
    naming_convention={
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    }
)

Base = declarative_base(metadata=metadata)


class SQLBaseModel(Base):

    __abstract__ = True
    __allow_unmapped__ = True

    id = Column(BigInteger(), primary_key=True)
