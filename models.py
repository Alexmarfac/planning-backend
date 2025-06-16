from datetime import date
from sqlalchemy import Column, Integer, String, ForeignKey, Date, Text
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class Sprint(Base):
    __tablename__ = 'sprints'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)

    pbis = relationship('PBI', back_populates='sprint', cascade='all, delete-orphan', lazy='selectin')

    def __repr__(self) -> str:
        return f"<Sprint(id={self.id}, name='{self.name}')>"

class PBI(Base):
    __tablename__ = 'pbis'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    sprint_id = Column(Integer, ForeignKey('sprints.id', ondelete='CASCADE'), nullable=True)

    sprint = relationship('Sprint', back_populates='pbis', lazy='joined')
    stories = relationship('Story', back_populates='pbi', cascade='all, delete-orphan', lazy='selectin')

    def __repr__(self) -> str:
        return f"<PBI(id={self.id}, title='{self.title}')>"

class Story(Base):
    __tablename__ = 'stories'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    raw_description = Column(Text, nullable=True)
    formatted_description = Column(Text, nullable=True)

    criticity = Column(Integer, nullable=True)  # 1: baja, 2: media, 3: alta
    story_points = Column(Integer, nullable=True)
    acceptance_criteria = Column(Text, nullable=True)
    priority = Column(Integer, nullable=True)   # 0: baja, 1: media, 2: alta
    business_value = Column(Integer, nullable=True)
    complexity = Column(Integer, nullable=True)
    story_type = Column(Integer, nullable=False, default=1)  # 1: usuario, 2: técnica
    continuation = Column(Integer, nullable=False, default=0)
    internal_dependencies = Column(Integer, nullable=False, default=0)

    pbi_id = Column(Integer, ForeignKey('pbis.id', ondelete='CASCADE'), nullable=False)
    pbi = relationship('PBI', back_populates='stories', lazy='joined')

    def __repr__(self) -> str:
        return f"<Story(id={self.id}, title='{self.title}')>"
