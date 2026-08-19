from .base import BaseDBModel, PyObjectId
from .materias import Materia, MateriaCreate, MateriaUpdate
from .provas import Prova, ProvaCreate, ProvaUpdate
from .usuarios import Usuario, UsuarioCreate, UsuarioUpdate, UsuarioResponse, UsuarioLogin, Token, Papel
from .duvidas import Duvida, DuvidaCreate, DuvidaUpdate, Comentario
from .mensagens import Mensagem, MensagemWSIn, MensagemUpdate
from .materiais_estudo import MaterialEstudo, MaterialEstudoCreate, MaterialEstudoUpdate
