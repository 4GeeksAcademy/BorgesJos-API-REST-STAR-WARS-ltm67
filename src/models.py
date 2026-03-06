from typing import List, Optional
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

db = SQLAlchemy()


class User(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(
        String(120), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean(), nullable=False)

    def serialize(self):
        return {
            "id": self.id,
            "email": self.email,
            # do not serialize the password, its a security breach
        }

# Modelado de Datos: Bolg Star Wars

# Tabla Users:


class Users(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    user_name: Mapped[str] = mapped_column(
        String(120), unique=True, nullable=False)
    first_name: Mapped[str] = mapped_column(
        String(120),  nullable=False)
    last_name: Mapped[str] = mapped_column(
        String(120),  nullable=False)
    email: Mapped[str] = mapped_column(
        String(120), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(nullable=False)
    suscription_day: Mapped[str] = mapped_column(
        String(120),  nullable=False)

    favorites_planets: Mapped[List["Favorites_planets"]
                              ] = relationship(back_populates="users")
    favorites_characters: Mapped[List["Favorites_characters"]] = relationship(
        back_populates="users")

    def serialize(self):
        return {
            "id": self.id,
            "user_name": self.user_name,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "password": self.password,
            "suscription_day": self.suscription_day

            # do not serialize the password, its a security breach
        }


# Tabla Planets:

class Planets(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(
        String(120), unique=True, nullable=False)
    rotation_period: Mapped[str] = mapped_column(
        String(120),  nullable=False)
    orbital_period: Mapped[str] = mapped_column(
        String(120),  nullable=False)
    climate: Mapped[str] = mapped_column(
        String(120),  nullable=False)
    population: Mapped[str] = mapped_column(nullable=False)

    favorites_planets: Mapped[List["Favorites_planets"]] = relationship(
        back_populates="planets"
    )

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "rotation_period": self.rotation_period,
            "orbital_period": self.orbital_period,
            "climate": self.climate,
            "population": self.population,
            # do not serialize the password, its a security breach
        }


# Tabla Characters:

class Characters(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(
        String(120),  nullable=False)
    type: Mapped[str] = mapped_column(
        String(120),  nullable=False)
    race: Mapped[str] = mapped_column(
        String(120),  nullable=False)
    height: Mapped[str] = mapped_column(
        String(120),  nullable=False)
    gender: Mapped[str] = mapped_column(nullable=False)

    favorites: Mapped[List["Favorites_characters"]] = relationship(
        back_populates="characters")

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "race": self.race,
            "height": self.height,
            "gender": self.gender,
            # do not serialize the password, its a security breach
        }


# Tabla Favorites_planets:

class Favorites_planets(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)

    # FK hacia Users (hijo de Users)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False
    )

    # FK hacia Planets (hijo de Planets)
    planet_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("planets.id"),
        nullable=False
    )

    # RELACIONES
    users: Mapped["Users"] = relationship(
        back_populates="favorites_planets"
    )

    planets: Mapped[Optional["Planets"]] = relationship(
        back_populates="favorites_planets"
    )

    def serialize(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "planet_id": self.planet_id,
        }


# Tabla Favorites_characters:

class Favorites_characters(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)

    # FK hacia Users (hijo de Users)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False
    )

    characters_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("characters.id"),
        nullable=False
    )

    # RELACIONES
    users: Mapped["Users"] = relationship(
        back_populates="favorites_characters"
    )

    characters: Mapped[Optional["Characters"]] = relationship(
        back_populates="favorites"
    )

    def serialize(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "character_id": self.character_id,
        }
