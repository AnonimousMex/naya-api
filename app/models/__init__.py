from app.models.game_history_archivements_model import GameHistoryAchievementsModel
from app.models.game_model import GameModel
from app.models.user_model import UserModel


UserModel.model_rebuild()
GameModel.model_rebuild()
GameHistoryAchievementsModel.model_rebuild()