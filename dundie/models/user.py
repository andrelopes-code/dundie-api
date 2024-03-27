from typing import Optional

from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    """
    Representa um usuário no sistema.

    Atributos:
    - id (Optional[int]): ID do usuário. Se None, não salvo no banco.
    - email (str): Endereço de e-mail único e não nulo.
    - username (str): Nome de usuário único e não nulo.
    - avatar (Optional[str]): URL da foto de perfil, pode ser nulo.
    - bio (Optional[str]): Breve descrição, pode ser nulo.
    - password (str): Senha do usuário, não nula.
    - name (str): Nome completo do usuário, não nulo.
    - dept (str): Departamento do usuário, não nulo.
    - currency (str): Moeda predominante do usuário, não nula.

    Métodos:
    - superuser (property): Retorna True se for superusuário,
    False caso contrário.
    """

    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, nullable=False)
    username: str = Field(unique=True, nullable=False)
    avatar: Optional[str] = None
    bio: Optional[str] = None
    password: str = Field(nullable=False)
    name: str = Field(nullable=False)
    dept: str = Field(nullable=False)
    currency: str = Field(nullable=False)

    @property
    def superuser(self):
        return self.dept == 'management'
