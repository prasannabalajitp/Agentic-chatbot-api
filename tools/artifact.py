import logging
from pathlib import Path
from uuid import uuid4

from langchain.tools import tool
from langchain_core.runnables import RunnableConfig

from common.tool_result import ToolResult
from core.constants import constants
from service.artifact_service import ArtifactService
from repository.artifact_repository import ArtifcatRepository
from tools.decorator import register_tool
from tools.tool_registry import ToolRisk

logger = logging.getLogger(__name__)

artifact_repository = ArtifcatRepository()
artifact_service = ArtifactService(artifact_repository=artifact_repository)


def artifact_impl(filename: str, content: str, content_type: str, context: dict) -> ToolResult:
    if not filename or not filename.strip():
        return {
            constants.SUMMARY: "A filename is required to create an artifact.",
            constants.CITATIONS: [],
            constants.METADATA: {
                constants.SUCC: False,
                constants.RETRYABLE: False,
            },
        }

    if not content or not content.strip():
        return {
            constants.SUMMARY: "Cannot create an artifact with empty content.",
            constants.CITATIONS: [],
            constants.METADATA: {
                constants.SUCC: False,
                constants.RETRYABLE: False,
            },
        }

    user_id = context.get(constants.USER_ID)
    if not user_id:
        return {
            constants.SUMMARY: "Unable to identify the current user.",
            constants.CITATIONS: [],
            constants.METADATA: {
                constants.SUCC: False,
                constants.RETRYABLE: False,
            },
        }

    safe_filename = Path(filename).name.strip()
    if safe_filename in {"", ".", ".."}:
        return {
            constants.SUMMARY: "The supplied filename is invalid.",
            constants.CITATIONS: [],
            constants.METADATA: {
                constants.SUCC: False,
                constants.RETRYABLE: False,
            },
        }

    artifact_path = None

    try:
        artifact_dir = Path(constants.ARTIFACT_DIR)
        artifact_dir.mkdir(parents=True, exist_ok=True)

        unique_name = f"{uuid4().hex}_{safe_filename}"
        artifact_path = artifact_dir / unique_name

        artifact_path.write_text(content, encoding="utf-8")

        artifact = artifact_service.create_artifact(
            user_id=user_id,
            file_path=str(artifact_path),
            filename=safe_filename,
            content_type=content_type or None,
        )

        return {
            constants.SUMMARY: (
                f"Artifact created successfully: {safe_filename}"
            ),
            constants.CITATIONS: [],
            constants.METADATA: {
                **artifact,
                constants.SUCC: True,
            },
        }

    except Exception:
        logger.exception("Artifact creation failed | filename=%s", safe_filename,)

        if artifact_path is not None:
            try:
                artifact_path.unlink(missing_ok=True)
            except OSError:
                logger.exception("Artifact cleanup failed | filename=%s", safe_filename)

        return {
            constants.SUMMARY: "The artifact could not be created right now.",
            constants.CITATIONS: [],
            constants.METADATA: {
                constants.SUCC: False,
                constants.RETRYABLE: True,
            },
        }


@register_tool(name=constants.ARTIFACT_TOOL_NAME, handler=artifact_impl, category=constants.UTLTY, risk=ToolRisk.MEDIUM)
@tool(parse_docstring=True, response_format=constants.RES_FORMAT)
def create_artifact_tool(filename: str, content: str, content_type: str, config: RunnableConfig) -> ToolResult:
    """Create a downloadable artifact from the provided content.

    Use this tool only when the user explicitly asks for a downloadable
    file, export, or file version of content.

    Args:
        filename: Name of the file to create.
        content: Content to write into the file.
        content_type: MIME type of the file.

    Returns:
        A message containing the artifact details.
    """
    configurable = config.get(constants.CONFIGURABLE, {})
    context = {
        constants.USER_ID: configurable.get(constants.USER_ID),
        constants.THREAD_ID: configurable.get(constants.THREAD_ID),
    }

    result = artifact_impl(filename=filename, content=content, content_type=content_type, context=context)

    return (
        result[constants.SUMMARY],
        result[constants.METADATA],
    )
