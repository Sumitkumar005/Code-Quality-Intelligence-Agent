"""
Notification manager for handling various notification types.
"""

from typing import Dict, List, Any, Optional
import asyncio
from datetime import datetime

from app.core.logging import get_logger
from app.core.config import settings

logger = get_logger(__name__)


class NotificationManager:
    """
    Manager for handling different types of notifications.
    """

    def __init__(self):
        self.notification_types = {
            'email': self._send_email_notification,
            'webhook': self._send_webhook_notification,
            'in_app': self._send_in_app_notification
        }

    async def send_notification(
        self,
        notification_type: str,
        recipient: str,
        subject: str,
        message: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Send a notification using the specified type.
        """
        try:
            if notification_type not in self.notification_types:
                return {
                    'success': False,
                    'error': f'Unsupported notification type: {notification_type}',
                    'notification_type': notification_type
                }

            handler = self.notification_types[notification_type]
            result = await handler(recipient, subject, message, metadata or {})

            logger.info(f"Notification sent: {notification_type} to {recipient}")

            return {
                'success': True,
                'notification_type': notification_type,
                'recipient': recipient,
                'timestamp': datetime.utcnow().isoformat(),
                **result
            }

        except Exception as e:
            logger.error(f"Notification failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'notification_type': notification_type,
                'recipient': recipient
            }

    async def send_analysis_complete_notification(
        self,
        user_email: str,
        project_name: str,
        analysis_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Send notification when analysis is complete.
        """
        try:
            issues_count = sum(len(result.get('issues', [])) for result in analysis_results.values())
            overall_score = analysis_results.get('overall_score', 0)

            subject = f"Analysis Complete: {project_name}"

            message = f"""
            Code analysis for project '{project_name}' has been completed.

            Summary:
            - Overall Score: {overall_score:.1f}/100
            - Total Issues Found: {issues_count}
            - Files Analyzed: {analysis_results.get('files_analyzed', 0)}

            View detailed results in your dashboard.
            """

            return await self.send_notification(
                'email',
                user_email,
                subject,
                message,
                {'project_name': project_name, 'analysis_results': analysis_results}
            )

        except Exception as e:
            logger.error(f"Analysis complete notification failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    async def send_report_generated_notification(
        self,
        user_email: str,
        report_id: str,
        report_type: str
    ) -> Dict[str, Any]:
        """
        Send notification when a report is generated.
        """
        try:
            subject = f"Report Generated: {report_type.title()}"

            message = f"""
            Your {report_type} report has been generated successfully.

            Report ID: {report_id}

            You can download the report from your dashboard.
            """

            return await self.send_notification(
                'email',
                user_email,
                subject,
                message,
                {'report_id': report_id, 'report_type': report_type}
            )

        except Exception as e:
            logger.error(f"Report generated notification failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    async def send_error_notification(
        self,
        user_email: str,
        error_type: str,
        error_message: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Send error notification.
        """
        try:
            subject = f"Error: {error_type}"

            message = f"""
            An error occurred in the system.

            Error Type: {error_type}
            Message: {error_message}

            Please check the system logs for more details.
            """

            return await self.send_notification(
                'email',
                user_email,
                subject,
                message,
                {'error_type': error_type, 'context': context or {}}
            )

        except Exception as e:
            logger.error(f"Error notification failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    async def send_batch_notifications(
        self,
        notifications: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Send multiple notifications.
        """
        results = []

        for notification in notifications:
            result = await self.send_notification(
                notification['type'],
                notification['recipient'],
                notification['subject'],
                notification['message'],
                notification.get('metadata')
            )
            results.append(result)

            # Small delay to avoid overwhelming services
            await asyncio.sleep(0.1)

        return results

    async def _send_email_notification(
        self,
        recipient: str,
        subject: str,
        message: str,
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Send email notification (placeholder implementation).
        """
        # In a real implementation, this would integrate with an email service
        # like SendGrid, AWS SES, or similar

        logger.info(f"Email notification would be sent to {recipient}: {subject}")

        return {
            'provider': 'email',
            'status': 'sent'
        }

    async def _send_webhook_notification(
        self,
        recipient: str,
        subject: str,
        message: str,
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Send webhook notification (placeholder implementation).
        """
        # In a real implementation, this would send HTTP POST to webhook URL

        logger.info(f"Webhook notification would be sent to {recipient}: {subject}")

        return {
            'provider': 'webhook',
            'status': 'sent'
        }

    async def _send_in_app_notification(
        self,
        recipient: str,
        subject: str,
        message: str,
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Send in-app notification (placeholder implementation).
        """
        # In a real implementation, this would store notification in database
        # and potentially send real-time notification via WebSocket

        logger.info(f"In-app notification would be sent to {recipient}: {subject}")

        return {
            'provider': 'in_app',
            'status': 'stored'
        }

    async def check_health(self) -> bool:
        """
        Check if notification services are healthy.
        """
        try:
            # Test basic notification sending
            test_result = await self.send_notification(
                'in_app',
                'test@example.com',
                'Health Check',
                'Testing notification service',
                {'test': True}
            )
            return test_result['success']
        except Exception:
            return False
