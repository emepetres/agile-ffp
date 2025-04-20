import pytest
from unittest.mock import patch, MagicMock

from agileffp.monitor.routes import Endpoints, init


class TestMonitorRoutes:
    """Test the Monitor Routes functionality."""

    def test_endpoints_with_prefix(self):
        """Test the with_prefix method of Endpoints enum."""
        # First, test with no prefix
        assert Endpoints.UPLOAD.with_prefix() == Endpoints.UPLOAD.value
        assert Endpoints.UPLOAD_TEMPLATE.with_prefix() == Endpoints.UPLOAD_TEMPLATE.value

        # Now, set the prefix and test again
        app = MagicMock()
        router = MagicMock()
        router.to_app = MagicMock()

        with patch('agileffp.monitor.routes.APIRouter') as mock_api_router:
            mock_api_router.return_value = router

            # Initialize with a prefix
            init(app, "charts_container_id", prefix="/test")

            # Verify the prefix is used
            assert Endpoints.UPLOAD.with_prefix() == "/test/upload"
            assert Endpoints.UPLOAD_TEMPLATE.with_prefix() == "/test/load_template"

            # Verify the router was initialized and attached to the app
            mock_api_router.assert_called_once_with(prefix="/test")
            router.to_app.assert_called_once_with(app)

    def test_init_with_controller(self):
        """Test the initialization with controller."""
        app = MagicMock()
        router = MagicMock()
        router.to_app = MagicMock()

        with patch('agileffp.monitor.routes.APIRouter') as mock_api_router, \
             patch('agileffp.monitor.routes.controller') as mock_controller:

            mock_api_router.return_value = router

            # Initialize with no prefix
            init(app, "charts_container_id")

            # Verify controller.init was called with the right parameters
            mock_controller.init.assert_called_once_with(router, Endpoints, "charts_container_id")

            # Verify the router was attached to the app
            router.to_app.assert_called_once_with(app)