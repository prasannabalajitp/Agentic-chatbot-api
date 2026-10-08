from pathlib import Path

from langchain.tools import tool
from langchain_core.runnables import RunnableConfig

from tools.decorator import register_tool
from core.constants import constants
from common.tool_result import ToolResult
from service.artifact_service import ArtifactService
from repository.artifact_repository import ArtifcatRepository
from tools.tool_registry import ToolRisk

artifact_repository = ArtifcatRepository()

artifact_service = ArtifactService(artifact_repository=artifact_repository)


def artifact_impl(filename: str, content: str, content_type: str, context: dict) -> ToolResult:

    try:
        if not content.strip():
            return {
                constants.SUMMARY: "Cannot create an artifact with empty content.",
                constants.CITATIONS: [],
                constants.METADATA: {},
            }

        user_id = context[constants.USER_ID]

        safe_filename = Path(filename).name
        artifact_dir = Path(constants.ARTIFACT_DIR)
        artifact_dir.mkdir(parents=True, exist_ok=True)
        file_path = artifact_dir/safe_filename

        file_path.write_text(content, encoding="utf-8",)

        # Register artifact
        artifact = artifact_service.create_artifact(
            user_id=user_id,
            file_path=str(file_path),
            filename=filename,
            content_type=content_type,
        )

        return {
            constants.SUMMARY: (
                f"Artifact created successfully: {filename}"
            ),
            constants.CITATIONS: [],
            constants.METADATA: artifact,
        }

    except Exception as ex:
        return {
            constants.SUMMARY: f"Failed to create artifact: {str(ex)}",
            constants.CITATIONS: [],
            constants.METADATA: {},
        }


@register_tool(name=constants.ARTIFACT_TOOL_NAME, handler=artifact_impl, category=constants.UTLTY, risk=ToolRisk.MEDIUM)
@tool(parse_docstring=True, response_format=constants.RES_FORMAT)
def create_artifact_tool(filename: str, content: str, content_type: str, config: RunnableConfig) -> ToolResult:
    """
    Create a downloadable artifact from the provided content.

    Use this tool only when the user explicitly asks for a
    downloadable file, export, or file version of content.

    Do not use this tool for normal responses.

    Args:
        filename: Name of the file to create.
        content: Content that should be written to the file.
        content_type: MIME type of the file.

    Returns:
        A message containing the created artifact details.
    """
    configurable = config.get(
        constants.CONFIGURABLE,
        {}
    )

    context = {
        constants.USER_ID: configurable[constants.USER_ID],
        constants.THREAD_ID: configurable[constants.THREAD_ID],
    }
    
    result = artifact_impl(
        filename=filename,
        content=content,
        content_type=content_type,
        context=context,
    )

    return (
        result[constants.SUMMARY],
        result[constants.METADATA],
    )
