from datetime import datetime, timezone, timedelta

from database.mongodb import usage_collection
from core.constants import constants


class UsageRepository:
    def __init__(self):
        self.collection = usage_collection

    def create_usage(self, usage: dict):
        usage[constants.CREATED_AT] = datetime.now(timezone.utc)
        result = self.collection.insert_one(usage)
        return result.inserted_id

    def get_user_usage(self, user_id: str):
        pipeline = [
            {
                constants.MATCH: {
                    constants.USER_ID: user_id
                }
            },
            {
                constants.GROUP: {
                    constants.ID: None,
                    constants.CONVERSATIONS: {
                        constants.ADD_SET: f"${constants.THREAD_ID}"
                    },
                    constants.MESSAGES: {
                        constants.SUM: 1
                    },
                    constants.INP_TKN: {
                        constants.SUM: f"${constants.INP_TKN}"
                    },
                    constants.OUT_TKN: {
                        constants.SUM: f"${constants.OUT_TKN}"
                    },
                    constants.TOT_TKN: {
                        constants.SUM: f"${constants.TOT_TKN}"
                    },
                    constants.TOOL_CALLS: {
                        constants.SUM: f"${constants.TOOL_CALLS}"
                    }
                }
            }
        ]

        result = list(self.collection.aggregate(pipeline))
        if not result:
            return {
                "conversations": 0,
                "messages": 0,
                "input_tokens": 0,
                "output_tokens": 0,
                "total_tokens": 0,
                "tool_calls": 0
            }

        data = result[0]

        return {
            "conversations": len(data.get("conversations", [])),
            "messages": data.get("messages", 0),
            "input_tokens": data.get("input_tokens", 0),
            "output_tokens": data.get("output_tokens", 0),
            "total_tokens": data.get("total_tokens", 0),
            "tool_calls": data.get("tool_calls", 0)
        }


    def get_token_usage(self, user_id: str, period: str = "7d"):
        days = self._get_period_days(period)
        start_date = (datetime.now(timezone.utc) - timedelta(days=days))

        pipeline = [
            {
                constants.MATCH: {
                    constants.USER_ID: user_id,
                    constants.CREATED_AT: {
                        constants.GTE: start_date
                    }
                }
            },
            {
                "$group": {
                    "_id": {
                        "$dateToString": {
                            "format": "%Y-%m-%d",
                            "date": f"${constants.CREATED_AT}"
                        }
                    },

                    "input_tokens": {
                        "$sum": f"${constants.INP_TKN}"
                    },

                    "output_tokens": {
                        "$sum": f"${constants.OUT_TKN}"
                    },

                    "total_tokens": {
                        "$sum": f"${constants.TOT_TKN}"
                    }
                }
            },
            {
                "$sort": {
                    "_id": 1
                }
            }
        ]

        result = list(self.collection.aggregate(pipeline))
        data = []

        for item in result:
            data.append(
                {
                    "date": item["_id"],
                    "input_tokens": item.get(
                        "input_tokens",
                        0
                    ),
                    "output_tokens": item.get(
                        "output_tokens",
                        0
                    ),
                    "total_tokens": item.get(
                        "total_tokens",
                        0
                    )
                }
            )

        return {
            "period": period,
            "data": data
        }

    def get_tool_usage(self, user_id: str):
        pipeline = [
            {
                "$match": {
                    constants.USER_ID: user_id
                }
            },
            {
                "$unwind": "$tools"
            },
            {
                "$group": {
                    "_id": "$tools",
                    "count": {
                        "$sum": 1
                    }
                }
            },
            {
                "$sort": {
                    "count": -1
                }
            }
        ]

        result = list(self.collection.aggregate(pipeline))
        tools = [
            {
                "name": item["_id"],
                "count": item["count"]
            }
            for item in result
        ]
        total_tool_calls = self._get_total_tool_calls(
            user_id=user_id
        )

        return {
            "total_tool_calls": total_tool_calls,
            "tools": tools
        }

    @staticmethod
    def _get_period_days(period: str) -> int:

        period_map = {
            "7d": 7,
            "30d": 30,
            "90d": 90,
        }

        if period not in period_map:
            raise ValueError(
                f"Unsupported usage period: {period}"
            )

        return period_map[period]

    def _get_total_tool_calls(self, user_id: str):

        result = self.collection.aggregate(
            [
                {
                    "$match": {
                        constants.USER_ID: user_id
                    }
                },
                {
                    "$group": {
                        "_id": None,
                        "total_tool_calls": {
                            "$sum": f"${constants.TOOL_CALLS}"
                        }
                    }
                }
            ]
        )

        result = list(result)

        if not result:
            return 0

        return result[0].get(
            "total_tool_calls",
            0
        )
