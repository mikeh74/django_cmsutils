from unittest.mock import MagicMock, Mock, patch

from django.test import RequestFactory, TestCase
from django.urls import Resolver404

from cmsutils.utils.utils import _resolve_cms_or_apphook


class ResolvesCmsOrApphookTestCase(TestCase):
    """Test that _resolve_cms_or_apphook returns valid page or apphook objects."""

    def setUp(self):
        self.factory = RequestFactory()
        self.request = self.factory.get("/test-path/")
        self.request.LANGUAGE_CODE = "en"

    @patch("cmsutils.utils.utils.applications_page_check")
    @patch("cmsutils.utils.utils.get_page_from_request")
    def test_returns_cms_page_when_page_exists_without_apphook(self, mock_get_page, mock_app_check):
        """Test that a CMS page without apphook is returned correctly."""
        mock_page = Mock()
        mock_page.application_urls = None
        mock_get_page.return_value = mock_page
        mock_app_check.return_value = None

        result = _resolve_cms_or_apphook(self.request)

        self.assertEqual(result["type"], "cms_page")
        self.assertIsNotNone(result["page"])
        self.assertEqual(result["page"], mock_page)
        self.assertEqual(result["object"], mock_page)
        self.assertIsNone(result["apphook"])
        mock_get_page.assert_called_once()

    @patch("cmsutils.utils.utils.apphook_pool")
    @patch("cmsutils.utils.utils.resolve")
    @patch("cmsutils.utils.utils.applications_page_check")
    @patch("cmsutils.utils.utils.get_page_from_request")
    def test_returns_apphook_when_page_has_apphook(
        self, mock_get_page, mock_app_check, mock_resolve, mock_apphook_pool
    ):
        """Test that a page with apphook is returned correctly."""
        mock_page = Mock()
        mock_page.application_urls = "test_apphook"
        mock_page.application_namespace = "test_namespace"
        mock_get_page.return_value = mock_page
        mock_app_check.return_value = None

        mock_apphook = Mock()
        mock_apphook.app_config = None
        mock_apphook_pool.get_apphook.return_value = mock_apphook

        mock_match = Mock()
        mock_match.func = Mock()
        mock_resolve.return_value = mock_match

        result = _resolve_cms_or_apphook(self.request)

        self.assertEqual(result["type"], "apphook")
        self.assertIsNotNone(result["page"])
        self.assertEqual(result["page"], mock_page)
        self.assertEqual(result["apphook"], "test_apphook")
        self.assertIsNotNone(result["apphook_instance"])
        self.assertIn("object", result)

    @patch("cmsutils.utils.utils.applications_page_check")
    @patch("cmsutils.utils.utils.get_page_from_request")
    def test_returns_not_found_when_no_page_exists(self, mock_get_page, mock_app_check):
        """Test that not_found is returned when neither page source finds a result."""
        mock_get_page.return_value = None
        mock_app_check.return_value = None

        result = _resolve_cms_or_apphook(self.request)

        self.assertEqual(result["type"], "not_found")
        self.assertIsNone(result["page"])
        self.assertIsNone(result["object"])
        self.assertIsNone(result["apphook"])

    @patch("cmsutils.utils.utils.applications_page_check")
    @patch("cmsutils.utils.utils.get_page_from_request")
    def test_falls_back_to_applications_page_check(self, mock_get_page, mock_app_check):
        """Test that applications_page_check is used when get_page_from_request fails."""
        mock_get_page.return_value = None
        mock_fallback_page = Mock()
        mock_fallback_page.application_urls = None
        mock_app_check.return_value = mock_fallback_page

        result = _resolve_cms_or_apphook(self.request)

        self.assertEqual(result["type"], "cms_page")
        self.assertEqual(result["page"], mock_fallback_page)
        self.assertEqual(result["object"], mock_fallback_page)

    @patch("cmsutils.utils.utils.apphook_pool")
    @patch("cmsutils.utils.utils.resolve")
    @patch("cmsutils.utils.utils.applications_page_check")
    @patch("cmsutils.utils.utils.get_page_from_request")
    def test_returns_valid_object_key(self, mock_get_page, mock_app_check, mock_resolve, mock_apphook_pool):
        """Test that the object key is never None when a page is found."""
        mock_page = Mock()
        mock_page.application_urls = None
        mock_get_page.return_value = mock_page

        result = _resolve_cms_or_apphook(self.request)

        # For cms_page type, object should be the page
        self.assertIsNotNone(result["object"])
        self.assertEqual(result["object"], mock_page)

    @patch("cmsutils.utils.utils.apphook_pool")
    @patch("cmsutils.utils.utils.resolve")
    @patch("cmsutils.utils.utils.applications_page_check")
    @patch("cmsutils.utils.utils.get_page_from_request")
    def test_returns_model_instance_when_view_has_get_object(
        self, mock_get_page, mock_app_check, mock_resolve, mock_apphook_pool
    ):
        """Test that model_instance is extracted when view has get_object method."""
        mock_page = Mock()
        mock_page.application_urls = "test_apphook"
        mock_page.application_namespace = "test_namespace"
        mock_get_page.return_value = mock_page

        mock_apphook = Mock()
        mock_apphook.app_config = None
        mock_apphook_pool.get_apphook.return_value = mock_apphook

        mock_view_class = Mock()
        mock_view_instance = Mock()
        mock_model_instance = Mock()
        mock_view_instance.get_object.return_value = mock_model_instance
        mock_view_class.return_value = mock_view_instance

        mock_match = Mock()
        mock_match.func = Mock(view_class=mock_view_class)
        mock_match.args = ()
        mock_match.kwargs = {}
        mock_resolve.return_value = mock_match

        result = _resolve_cms_or_apphook(self.request)

        self.assertEqual(result["model_instance"], mock_model_instance)
        self.assertEqual(result["object"], mock_model_instance)

    @patch("cmsutils.utils.utils.apphook_pool")
    @patch("cmsutils.utils.utils.resolve")
    @patch("cmsutils.utils.utils.applications_page_check")
    @patch("cmsutils.utils.utils.get_page_from_request")
    def test_returns_none_object_when_apphook_has_no_model_instance(
        self, mock_get_page, mock_app_check, mock_resolve, mock_apphook_pool
    ):
        """Test that object is None when apphook exists but no model instance found."""
        mock_page = Mock()
        mock_page.application_urls = "test_apphook"
        mock_page.application_namespace = "test_namespace"
        mock_get_page.return_value = mock_page

        mock_apphook = Mock()
        mock_apphook.app_config = None
        mock_apphook_pool.get_apphook.return_value = mock_apphook

        # Simulate URL resolution that doesn't return a view with get_object
        mock_match = Mock()
        mock_match.func = Mock(spec=[])  # No view_class attribute
        mock_resolve.return_value = mock_match

        result = _resolve_cms_or_apphook(self.request)

        # When apphook has no model instance, object should be None
        # This indicates the URL cannot be properly processed for updates
        self.assertEqual(result["type"], "apphook")
        self.assertIsNotNone(result["page"])
        self.assertIsNone(result["object"], "object should be None when apphook has no model_instance")


from django.contrib.auth.models import User
from cmsutils.models import PageUpdates


class PageUpdatesApplyTestCase(TestCase):
    """Test that PageUpdates.apply method handles various scenarios correctly."""

    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass")

    @patch("cmsutils.models.get_object_from_url")
    def test_apply_fails_when_object_not_found(self, mock_get_object):
        """Test that apply fails when the URL cannot be resolved."""
        mock_get_object.return_value = {
            "type": "not_found",
            "page": None,
            "object": None,
            "apphook": None,
        }

        page_update = PageUpdates.objects.create(
            page_url="http://example.com/invalid-page/",
            title="Test Title",
            description="Test Description",
            upload_user=self.user,
        )

        succeeded, message = page_update.apply(self.user)

        self.assertFalse(succeeded)
        self.assertIn("could not be found", message)
        self.assertIsNotNone(page_update.failed_at)

    @patch("cmsutils.models.get_object_from_url")
    def test_apply_fails_when_apphook_has_no_model_instance(self, mock_get_object):
        """Test that apply fails when apphook is found but no model instance exists."""
        mock_page = Mock()
        mock_page.application_urls = "test_apphook"

        mock_get_object.return_value = {
            "type": "apphook",
            "page": mock_page,
            "object": None,  # No model instance
            "apphook": "test_apphook",
            "model_instance": None,
        }

        page_update = PageUpdates.objects.create(
            page_url="http://example.com/apphook/",
            title="Test Title",
            description="Test Description",
            upload_user=self.user,
        )

        succeeded, message = page_update.apply(self.user)

        self.assertFalse(succeeded)
        self.assertIn("could not be found", message)
        self.assertIsNotNone(page_update.failed_at)
