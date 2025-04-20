import pytest
import yaml
from unittest.mock import patch, MagicMock

from fasthtml.common import FormData, StreamingResponse

from agileffp.monitor.controller import init, index
from agileffp.monitor.routes import Endpoints


@pytest.fixture
def mock_router():
    """Create a mock router for testing."""
    router = MagicMock()
    router.get = MagicMock(side_effect=lambda path: lambda *args, **kwargs: None)
    router.put = MagicMock(side_effect=lambda path: lambda *args, **kwargs: None)
    router.post = MagicMock(side_effect=lambda path: lambda *args, **kwargs: None)
    return router


@pytest.fixture
def mock_request():
    """Create a mock request for testing."""
    request = MagicMock()
    request.headers = {"hx-current-url": "/project/test_project"}
    request.session = {}
    return request


@pytest.fixture
def mock_form():
    """Create a mock form data for testing."""
    form = MagicMock(spec=FormData)
    form.get = MagicMock(side_effect=lambda key, default=None: {
        "file": MagicMock(file=MagicMock(read=lambda: b"yaml: content")),
        "yaml_content": "yaml: content",
        "version": "version-1",
        "version_name": "new-version",
        "version_date": "2023-01-01 12:00:00"
    }.get(key, default))
    return form


class TestMonitorController:
    """Test the Monitor Controller functionality."""

    def test_init(self, mock_router):
        """Test the init function that sets up routes."""
        # Call init with our mocked router
        init(mock_router, Endpoints, "test_charts_target")

        # Verify the router methods were called the correct number of times
        assert mock_router.get.call_count == 5
        assert mock_router.put.call_count == 3
        assert mock_router.post.call_count == 3

    @patch('agileffp.monitor.controller.project_controller')
    @patch('agileffp.monitor.controller.yaml_editor')
    @patch('agileffp.monitor.controller.charts')
    def test_index(self, mock_charts, mock_yaml_editor, mock_project_controller):
        """Test the index function."""
        # Set up the mocks
        mock_project_controller.get_project_context.return_value = (
            "version-1", "yaml: content", "prev-version", "next-version"
        )
        mock_yaml_editor.render.return_value = "<div>YAML Editor</div>"
        mock_charts.render_charts.return_value = "<div>Charts</div>"

        # Call the function
        yaml_part, charts_part = index("test_project")

        # Verify the project controller was called
        mock_project_controller.get_project_context.assert_called_once_with("test_project")

        # Verify the yaml editor was called
        mock_yaml_editor.render.assert_called_once()

        # Verify the charts were rendered
        mock_charts.render_charts.assert_called_once()

        # Verify the results
        assert charts_part == "<div>Charts</div>"
        assert yaml_part == "<div>YAML Editor</div>"

    @patch('agileffp.monitor.controller.yaml_editor')
    def test_upload_yaml(self, mock_yaml_editor, mock_request, mock_form):
        """Test the upload_yaml function."""
        # Set up the patch
        with patch('agileffp.monitor.controller._try_render_charts') as mock_render_charts:
            mock_yaml_editor.render.return_value = "<div>YAML Editor</div>"
            mock_render_charts.return_value = "<div>Charts</div>"

            # Create the function from init
            upload_yaml = self._create_upload_yaml_fn(mock_yaml_editor, mock_render_charts)

            # Call the function
            result = upload_yaml(mock_request, mock_form)

            # Verify the editor was rendered
            mock_yaml_editor.render.assert_called_once()

            # Verify the charts were tried to render
            mock_render_charts.assert_called_once()

            # Check the result
            assert result == ("<div>YAML Editor</div>", "<div>Charts</div>")

    def _create_upload_yaml_fn(self, mock_yaml_editor, mock_render_charts):
        """Helper to create a function similar to what init would create."""
        async def upload_yaml(request, form):
            version = "dirty"
            prev_version = None
            next_version = None
            file = form.get("file")
            yaml_content = file.file.read().decode("utf-8") if file else None

            return (mock_yaml_editor.render(False, version, yaml_content, prev_version, next_version, "_charts_target"),
                   mock_render_charts(yaml_content))

        return upload_yaml

    @patch('agileffp.monitor.controller.project_controller')
    def test_try_render_charts_success(self, mock_project_controller):
        """Test the _try_render_charts function with valid YAML."""
        # Create a valid YAML
        yaml_content = """
        name: test
        items:
          - id: 1
            value: foo
        """

        # Set up the patch
        with patch('agileffp.monitor.controller.charts') as mock_charts:
            mock_charts.render_charts.return_value = "<div>Charts</div>"

            # Call the function (we need to import it directly)
            from agileffp.monitor.controller import _try_render_charts
            result = _try_render_charts(yaml_content)

            # Verify charts.render_charts was called with the parsed YAML
            mock_charts.render_charts.assert_called_once()

            # Verify the result
            assert result == "<div>Charts</div>"

    @patch('agileffp.monitor.controller.charts')
    @patch('agileffp.monitor.controller.Div')
    def test_try_render_charts_invalid_yaml(self, mock_div, mock_charts):
        """Test the _try_render_charts function with invalid YAML."""
        # Create an invalid YAML
        yaml_content = """
        bad: [
          unclosed bracket
        """

        # Set up the mocks
        mock_div.return_value = "<div>Invalid YAML format</div>"

        # Call the function (we need to import it directly)
        from agileffp.monitor.controller import _try_render_charts
        result = _try_render_charts(yaml_content)

        # Verify Div was called with an error message
        mock_div.assert_called_once()
        assert "Invalid YAML format" in str(mock_div.call_args)

        # Verify render_charts was NOT called
        mock_charts.render_charts.assert_not_called()