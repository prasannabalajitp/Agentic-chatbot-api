class Constants:

    #users.py
    USERS = "users"


    #auth.py
    AUTH = "Authentication"


    #message.py
    NO = "no"
    CONN = "Connection"
    MESSAGES = "messages"
    NO_CACHE = "no-cache"
    KEEP_ALIVE = "keep-alive"
    CACHE_CONTROL = "Cache-Control"
    MEDIA_TYPE = "text/event-stream"
    BUFFERING = "X-Accel-Buffering"

    #nvidia_llm.py
    TITLE_MDL = "meta/llama-3.2-3b-instruct"
    RAG_MDL = "meta/llama-3.3-70b-instruct"
    REASONING = "reasoning"
    RSNG_API_FLDS = "_reasoning_api_fields"
    

    #mongodb.py
    FILE = "file"
    THREADS = "threads"
    REF_TKN = "refresh_tokens"
    CHECKPOINTS = "checkpoints"
    FILE_VECTORS = "file_vectors"
    CONVERSATIONS = "conversations"
    CHECKPOINTS_WRITES = "checkpoint_writes"


    #user_repository.py
    NAME = "name"
    EMAIL = "email"
    MATCHED = "matched"
    HASHED_PWD = "hashed_password"


    #chatbot_graph.py
    TOOLS = "tools"
    MAX_HISTORY = 10
    THINK = "<think>"
    CHATBOT = "chatbot"
    USER_ID = "user_id"
    THREAD_ID = "thread_id"
    CONFIGURABLE = "configurable"
    STRF_TIME = "%d-%m-%Y %H:%M:%S"
    RSNG_CNTNT = "reasoning_content"
    DUP_ENTRY = "Duplicate tool detected. Ending graph."


    #request_model.py
    USR_QRY = "User query"
    USR_IDENTIFIER = "User identifier"
    DEFAULT_TITLE = "New Conversation"
    CRET_USR_DESC = "Unique user identifier"
    CONV_IDENTIFIER = "Conversation thread identifier"


    #conversation_repository.py
    ID = "_id"
    SET = "$set"
    INC = "$inc"
    TITLE = "title"
    CREATED_AT = "created_at"
    UPDATED_AT = "updated_at"
    MSG_COUNT = "message_count"
    LST_MSG_AT = "last_message_at"
    

    #security.py
    EXP = "exp"
    TYPE = "type"
    BCRYPT = "bcrypt"
    ACCESS = "access"
    REFRESH = "refresh"
    INVALID_TKN = "Invalid or expired token"
    

    #document_parser_service.py
    DOT = "."
    PDF = "pdf"
    TXT_EXT = ".txt"
    UTF_EXT = "utf-8"
    PDF_EXT = ".pdf"
    DOCX_EXT = ".docx"


    #chat_history_service.py
    AI = "ai"
    HUMAN = "human"
    CONTENT = "content"
    CHANL_VALUES = "channel_values"
    TOOL_CALLS = "tool_calls"


    #admin_service.py
    USER = "user"
    ADM = "admin"
    MODIFIED = "modified"
    INVALID_ROLE = "Invalid Role"
    USR_NOT_FOUND = "User not found."
    THRD_NOT_FOUND = "Thread not found."
    USR_DEL_SUC = "User Deleted Successfully."
    USR_ROL_UPDATED = "User role updated successfully."
    CONV_DEL_SUC = "Conversation deleted successfully."
    

    #file_service.py    
    FILE_NOT_FOUND = "File not found."
    NO_FILES = "No files found for this user"
    FILE_DEL_SUC = "File Deleted Successfully."


    #user_service.py
    USR_EXISTS = "User already exists"


    #conversation_service.py
    V2 = "v2"
    MDL = "model"
    DATA = "data"
    TOOL = "tool"
    ERR = "error"
    DONE = "done"
    QUERY = "query"
    CHUNK = "chunk"
    INPUT = "input"
    EVENT = "event"
    MSG = "message"
    TS = "timestamp"
    EMPTY_STRING = ""    
    OUTPUT = "output"
    ARGS = "arguments"
    
    CMPLTD = "completed"
    RESPONSE = "response"
    LLM_CHUNK = "llm_chunk"
    TOOL_CALL = "tool_call"
    TOOL_ID = "tool_call_id"
    CHART_STRT = "chat_start"
    ON_TOOL_END = "on_tool_end"
    TOOL_RESP = "tool_response"
    FNSH_RESON = "finish_reason"
    ON_TOOL_START = "on_tool_start"
    CHART_MDL_END = "chat_model_end"
    CHART_MDL_STRT = "chat_model_start"
    CONV_ACTY = "conversation_activity"
    CONV_UPDATED = "conversation_updated"
    ON_CHAT_MDL_STRM = "on_chat_model_stream"
    LMT_EXCP = "Limit must be between 1 and 100"
    STREAMING_MDL = "meta/llama-3.1-8b-instruct"
    PAGE_EXCP = "Page number must be greater than 0"
    CONVERSATION_NOT_FOUND = "Conversation not found."
    CONV_HST_SUC = "Conversation history cleared successfully."
    CONV_TITLE_NAME_EXCP = "Conversation title cannot be empty"
    CONV_TITLE_EXCP = "Conversation title cannot exceed 100 characters."
    

    #document_parser_service.py
    ALLOWED_EXT = {".txt", ".pdf", ".docx"}

    
    #user_service.py
    SUB = "sub"
    PAGE = "page"
    ITEMS = "items"
    LIMIT = "limit"
    TOTAL = "total"
    HAS_NXT = "has_next"
    TTL_PAGES = "total_pages"
    HAS_PREV = "has_previous"
    LOG_OUT_SUC = "Logged out successfully."
    LOG_OUT_ALL = "Logged out from all devices."
    INVALID_UNAME_PWD = "Invalid Username or password"


    #weather_service.py
    BDY = 'body'
    AUTO = "auto"
    HREF = 'href'
    URL = "url"
    RESULTS = "results"
    CURRENT = "current"
    TIMEZONE = "timezone"
    LATITUDE = "latitude"
    LONGITUDE = "longitude"
    TEMP_VALUES = [
                        "temperature_2m",
                        "relative_humidity_2m",
                        "apparent_temperature",
                        "is_day",
                        "precipitation",
                        "rain",
                        "weather_code",
                        "wind_speed_10m"
                    ]
    

    #refresh_token_repository.py
    GT = "$gt"
    LT = "$lt"
    EXP_AT = "expires_at"
    TKN_HSH = "token_hash"
    IS_REV = "is_revoked"
    

    #file_repository.py
    SIZE = "size"
    FILE_ID = "file_id"
    UPLOADED = "uploaded"
    FILE_STATUS = "status"
    FILE_NAME = "file_name"
    CONTENT_TYPE = "content_type"
    

    #web_search_service.py
    NO_RSLTS_FND = "No search results found."
    CNTXT = "context"
    CITATIONS = "citations"
    
    
    #dependencies.py
    ROLE = "role"
    FORBIDDEN = "You don't have permission to perform this action."
    

    #ai_search.py
    NO_REL_DOC = "No relevant documents found."
    USER_DOC_EMPTY = "No documents have been uploaded for this conversation yet. \nPlease upload your documents first."
    AI_SRCH = "ai_search"
    UTLTY = "utility"

    #calculator.py
    CALC = "calculator"

    #datetime.py
    CUR_DT = "current datetime"

    #web_search.py
    WEB_SRCH = "web_search"

    #tool_registry.py
    GEN = "general"

    #list_uploaded_files.py
    UPLD_FILES = "list_uploaded_files"


    #embedding_service.py
    TXT = "text"
    CHUNK_SIZE = 1000
    CHUNK_OVERLAP = 200
    EMBDNG = "embedding"
    CHUNK_ID = "chunk_id"
    CHUNK_IDX = "chunk_index"
    EMB_FAIL = "Failed to generate embeddings"
    INVALID_TXT = "The uploaded document does not contain extractable text."

    #prompt_guardrail.py
    SUSPICIOUS_PATTERNS = [
        "ignore previous instructions",
        "system prompt",
        "developer prompt",
        "hidden instructions",
        "tool registry",
        "internal tool",
        "reveal prompt",
        "jailbreak",
    ]
    BLOCKED_TERMS = [
        "system prompt",
        "api_key",
        "secret_key",
        "internal server error",
        "traceback"
    ]
    UNABLE_VALIDATE = "Unable to validate prompt."
    UNSFE_PRMPT = "Unsafe prompt detected."
    UNSFE_RESP = "Unsafe response generated."
    ALLWD = "allowed"
    REASON = "reason"

    #tool_guardrail.py
    MNY_TOOL_CALL = "Too many tool calls."


constants = Constants()
