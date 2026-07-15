from datetime import datetime, timezone
from database.mongodb import refresh_tokens_collection
from core.constants import constants


class RefreshTokenRepository:

    def __init__(self):
        self.collection = refresh_tokens_collection

    
    def save_refresh_token(self, user_id: str, token_hash: str, expires_at: datetime):
        document = {
            constants.USER_ID: user_id,
            constants.TKN_HSH: token_hash,
            constants.CREATED_AT: datetime.now(timezone.utc),
            constants.UPDATED_AT: datetime.now(timezone.utc),
            constants.EXP_AT: expires_at,
            constants.IS_REV: False
        }
        self.collection.insert_one(document)
        return document
    

    def get_refresh_tokens(self, user_id: str):
        return list(
            self.collection.find({
                constants.USER_ID: user_id
            },
            {
                constants.ID: 0
            }).sort(constants.CREATED_AT, -1)
        )
    
    def get_active_refresh_tokens(self, user_id: str):
        return list(
            self.collection.find(
                {
                    constants.USER_ID: user_id,
                    constants.IS_REV: False,
                    constants.EXP_AT: {constants.GT: datetime.now(timezone.utc)}
                },
                {
                    constants.ID: 0
                }
            )
        )
    
    def revoke_refresh_token(self, token_hash: str):
        return self.collection.update_one(
            {
                constants.TKN_HSH: token_hash,
                constants.IS_REV: False
            },
            {
                constants.SET: {
                    constants.IS_REV: True
                }
            }
        )
    
    def revoke_all_refresh_tokens(self, user_id: str):
        return self.collection.update_many(
            {
                constants.USER_ID: user_id,
                constants.IS_REV: False,
                constants.EXP_AT: {constants.GT: datetime.now(timezone.utc)}
            },
            {
                constants.SET: {
                    constants.IS_REV: True
                }
            }
        )
    
    def delete_expired_tokens(self):
        return self.collection.delete_many(
            {
                constants.EXP_AT: {
                    constants.LT: datetime.now(timezone.utc)
                }
            }
        )
    
    def get_refresh_token(self, token_hash: str):
        return self.collection.find_one(
            {
                constants.TKN_HSH: token_hash,
                constants.IS_REV: False,
                constants.EXP_AT: {constants.GT: datetime.now(timezone.utc)}
            },
            {
                constants.ID: 0
            }
        )
