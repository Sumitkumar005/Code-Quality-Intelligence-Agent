"""
Email notification service for sending emails.
"""

import asyncio
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import Dict, List, Any, Optional, BinaryIO
from datetime import datetime

from app.core.logging import get_logger
from app.core.config import settings

logger = get_logger(__name__)


class EmailService:
    """
    Service for sending email notifications.
    """

    def __init__(
        self,
        smtp_server: Optional[str] = None,
        smtp_port: Optional[int] = None,
        smtp_username: Optional[str] = None,
        smtp_password: Optional[str] = None,
        from_email: Optional[str] = None,
        from_name: Optional[str] = None
    ):
        self.smtp_server = smtp_server or settings.SMTP_SERVER or "smtp.gmail.com"
        self.smtp_port = smtp_port or settings.SMTP_PORT or 587
        self.smtp_username = smtp_username or settings.SMTP_USERNAME
        self.smtp_password = smtp_password or settings.SMTP_PASSWORD
        self.from_email = from_email or settings.FROM_EMAIL or "noreply@cqia.com"
        self.from_name = from_name or settings.FROM_NAME or "Code Quality Intelligence Agent"

    async def send_email(
        self,
        to_email: str,
        subject: str,
        body: str,
        html_body: Optional[str] = None,
        cc_emails: Optional[List[str]] = None,
        bcc_emails: Optional[List[str]] = None,
        attachments: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Send an email.
        """
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = f"{self.from_name} <{self.from_email}>"
            msg['To'] = to_email
            msg['Subject'] = subject

            if cc_emails:
                msg['Cc'] = ', '.join(cc_emails)

            if bcc_emails:
                msg['Bcc'] = ', '.join(bcc_emails)

            # Add body
            if html_body:
                # HTML email
                msg.attach(MIMEText(body, 'plain'))
                msg.attach(MIMEText(html_body, 'html'))
            else:
                # Plain text email
                msg.attach(MIMEText(body, 'plain'))

            # Add attachments
            if attachments:
                for attachment in attachments:
                    await self._add_attachment(msg, attachment)

            # Send email
            await self._send_message(msg, to_email, cc_emails, bcc_emails)

            return {
                'success': True,
                'to_email': to_email,
                'subject': subject,
                'sent_at': datetime.utcnow().isoformat(),
                'message_id': f"msg_{datetime.utcnow().timestamp()}"
            }

        except Exception as e:
            logger.error(f"Email sending failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'to_email': to_email,
                'subject': subject
            }

    async def _add_attachment(
        self,
        msg: MIMEMultipart,
        attachment: Dict[str, Any]
    ) -> None:
        """
        Add attachment to email message.
        """
        try:
            filename = attachment['filename']
            file_data = attachment['data']
            content_type = attachment.get('content_type', 'application/octet-stream')

            # Create attachment part
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(file_data)
            encoders.encode_base64(part)
            part.add_header(
                'Content-Disposition',
                f'attachment; filename="{filename}"'
            )
            part.add_header('Content-Type', content_type)

            msg.attach(part)

        except Exception as e:
            logger.error(f"Attachment addition failed: {e}")
            raise

    async def _send_message(
        self,
        msg: MIMEMultipart,
        to_email: str,
        cc_emails: Optional[List[str]] = None,
        bcc_emails: Optional[List[str]] = None
    ) -> None:
        """
        Send email message via SMTP.
        """
        try:
            # Create recipient list
            recipients = [to_email]
            if cc_emails:
                recipients.extend(cc_emails)
            if bcc_emails:
                recipients.extend(bcc_emails)

            # Send email
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.smtp_username, self.smtp_password)
            server.sendmail(self.from_email, recipients, msg.as_string())
            server.quit()

        except Exception as e:
            logger.error(f"SMTP sending failed: {e}")
            raise

    async def send_analysis_report_email(
        self,
        to_email: str,
        project_name: str,
        analysis_results: Dict[str, Any],
        report_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send analysis report email.
        """
        try:
            subject = f"Code Quality Analysis Report - {project_name}"

            # Calculate summary
            summary = analysis_results.get('summary', {})
            score = summary.get('overall_score', 0)
            grade = summary.get('grade', 'Unknown')
            total_issues = summary.get('total_issues', 0)

            body = f"""
            Dear User,

            Your code quality analysis for project "{project_name}" has been completed.

            Analysis Summary:
            - Overall Score: {score:.1f}/100 (Grade: {grade})
            - Total Issues Found: {total_issues}
            - Files Analyzed: {summary.get('total_files', 0)}

            """

            if score >= 90:
                body += "Excellent! Your code quality is outstanding.\n\n"
            elif score >= 80:
                body += "Great job! Your code quality is very good.\n\n"
            elif score >= 70:
                body += "Good work! Your code quality is above average.\n\n"
            elif score >= 60:
                body += "Your code quality is acceptable but could be improved.\n\n"
            else:
                body += "Your code quality needs significant improvement.\n\n"

            if report_url:
                body += f"View detailed report: {report_url}\n\n"

            body += """
            Best regards,
            Code Quality Intelligence Agent
            """

            html_body = f"""
            <html>
            <body>
                <h2>Code Quality Analysis Report</h2>
                <p>Dear User,</p>

                <p>Your code quality analysis for project <strong>{project_name}</strong> has been completed.</p>

                <div style="background-color: #f0f0f0; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <h3>Analysis Summary</h3>
                    <ul>
                        <li><strong>Overall Score:</strong> {score:.1f}/100 (Grade: {grade})</li>
                        <li><strong>Total Issues Found:</strong> {total_issues}</li>
                        <li><strong>Files Analyzed:</strong> {summary.get('total_files', 0)}</li>
                    </ul>
                </div>

                <p>"""

            if score >= 90:
                html_body += "<span style='color: green; font-weight: bold;'>Excellent! Your code quality is outstanding.</span>"
            elif score >= 80:
                html_body += "<span style='color: blue; font-weight: bold;'>Great job! Your code quality is very good.</span>"
            elif score >= 70:
                html_body += "<span style='color: orange; font-weight: bold;'>Good work! Your code quality is above average.</span>"
            else:
                html_body += "<span style='color: red; font-weight: bold;'>Your code quality needs significant improvement.</span>"

            html_body += "</p>"

            if report_url:
                html_body += f"<p><a href='{report_url}' style='background-color: #007cba; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;'>View Detailed Report</a></p>"

            html_body += """
                <p>Best regards,<br>
                <strong>Code Quality Intelligence Agent</strong></p>
            </body>
            </html>
            """

            return await self.send_email(
                to_email=to_email,
                subject=subject,
                body=body,
                html_body=html_body
            )

        except Exception as e:
            logger.error(f"Analysis report email failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'to_email': to_email,
                'project_name': project_name
            }

    async def send_security_alert_email(
        self,
        to_email: str,
        project_name: str,
        security_issues: List[Dict[str, Any]],
        severity: str = "high"
    ) -> Dict[str, Any]:
        """
        Send security alert email.
        """
        try:
            subject = f"🚨 Security Alert - {project_name} ({severity} severity)"

            body = f"""
            Dear User,

            Security vulnerabilities have been detected in your project "{project_name}".

            Severity: {severity.upper()}
            Issues Found: {len(security_issues)}

            Critical Issues:
            """

            html_body = f"""
            <html>
            <body>
                <h2 style="color: #e74c3c;">🚨 Security Alert</h2>
                <p>Dear User,</p>

                <p>Security vulnerabilities have been detected in your project <strong>{project_name}</strong>.</p>

                <div style="background-color: #ffebee; padding: 15px; border-radius: 5px; margin: 20px 0; border-left: 4px solid #e74c3c;">
                    <h3>Alert Details</h3>
                    <ul>
                        <li><strong>Severity:</strong> {severity.upper()}</li>
                        <li><strong>Issues Found:</strong> {len(security_issues)}</li>
                    </ul>
                </div>

                <h3>Critical Issues:</h3>
                <table style="width: 100%; border-collapse: collapse;">
                    <tr style="background-color: #f5f5f5;">
                        <th style="padding: 10px; border: 1px solid #ddd;">Issue</th>
                        <th style="padding: 10px; border: 1px solid #ddd;">File</th>
                        <th style="padding: 10px; border: 1px solid #ddd;">Line</th>
                        <th style="padding: 10px; border: 1px solid #ddd;">Severity</th>
                    </tr>
            """

            for issue in security_issues[:10]:  # Limit to first 10 issues
                body += f"- {issue.get('title', 'Unknown issue')}\n"
                html_body += f"""
                    <tr>
                        <td style="padding: 10px; border: 1px solid #ddd;">{issue.get('title', 'Unknown issue')}</td>
                        <td style="padding: 10px; border: 1px solid #ddd;">{issue.get('file', 'Unknown file')}</td>
                        <td style="padding: 10px; border: 1px solid #ddd;">{issue.get('line', 'N/A')}</td>
                        <td style="padding: 10px; border: 1px solid #ddd;">{issue.get('severity', 'unknown')}</td>
                    </tr>
                """

            body += """
            Please review and address these security issues immediately.

            Best regards,
            Code Quality Intelligence Agent Security Team
            """

            html_body += """
                </table>

                <div style="background-color: #fff3cd; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <p><strong>⚠️ Action Required:</strong> Please review and address these security issues immediately.</p>
                </div>

                <p>Best regards,<br>
                <strong>Code Quality Intelligence Agent Security Team</strong></p>
            </body>
            </html>
            """

            return await self.send_email(
                to_email=to_email,
                subject=subject,
                body=body,
                html_body=html_body
            )

        except Exception as e:
            logger.error(f"Security alert email failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'to_email': to_email,
                'project_name': project_name
            }

    async def send_weekly_digest_email(
        self,
        to_email: str,
        projects_data: List[Dict[str, Any]],
        week_start: datetime,
        week_end: datetime
    ) -> Dict[str, Any]:
        """
        Send weekly digest email.
        """
        try:
            subject = f"Weekly Code Quality Digest - {week_start.strftime('%B %d')} to {week_end.strftime('%B %d, %Y')}"

            body = f"""
            Dear User,

            Here's your weekly code quality digest for {len(projects_data)} projects.

            Weekly Summary:
            - Projects Analyzed: {len(projects_data)}
            - Average Score: {sum(p.get('score', 0) for p in projects_data) / max(len(projects_data), 1):.1f}
            - Total Issues: {sum(p.get('issues_count', 0) for p in projects_data)}

            Project Breakdown:
            """

            html_body = f"""
            <html>
            <body>
                <h2>Weekly Code Quality Digest</h2>
                <p>Dear User,</p>

                <p>Here's your weekly code quality digest for <strong>{len(projects_data)} projects</strong>.</p>

                <div style="background-color: #f0f0f0; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <h3>Weekly Summary</h3>
                    <ul>
                        <li><strong>Projects Analyzed:</strong> {len(projects_data)}</li>
                        <li><strong>Average Score:</strong> {sum(p.get('score', 0) for p in projects_data) / max(len(projects_data), 1):.1f}</li>
                        <li><strong>Total Issues:</strong> {sum(p.get('issues_count', 0) for p in projects_data)}</li>
                    </ul>
                </div>

                <h3>Project Breakdown</h3>
                <table style="width: 100%; border-collapse: collapse;">
                    <tr style="background-color: #f5f5f5;">
                        <th style="padding: 10px; border: 1px solid #ddd;">Project</th>
                        <th style="padding: 10px; border: 1px solid #ddd;">Score</th>
                        <th style="padding: 10px; border: 1px solid #ddd;">Grade</th>
                        <th style="padding: 10px; border: 1px solid #ddd;">Issues</th>
                        <th style="padding: 10px; border: 1px solid #ddd;">Trend</th>
                    </tr>
            """

            for project in projects_data:
                body += f"- {project.get('name', 'Unknown')}: Score {project.get('score', 0):.1f} ({project.get('grade', 'N/A')})\n"
                trend_indicator = "↗️" if project.get('trend') == 'up' else "↘️" if project.get('trend') == 'down' else "➡️"

                html_body += f"""
                    <tr>
                        <td style="padding: 10px; border: 1px solid #ddd;">{project.get('name', 'Unknown')}</td>
                        <td style="padding: 10px; border: 1px solid #ddd;">{project.get('score', 0):.1f}</td>
                        <td style="padding: 10px; border: 1px solid #ddd;">{project.get('grade', 'N/A')}</td>
                        <td style="padding: 10px; border: 1px solid #ddd;">{project.get('issues_count', 0)}</td>
                        <td style="padding: 10px; border: 1px solid #ddd;">{trend_indicator}</td>
                    </tr>
                """

            body += """
            Keep up the good work!

            Best regards,
            Code Quality Intelligence Agent
            """

            html_body += """
                </table>

                <p>Keep up the good work!</p>

                <p>Best regards,<br>
                <strong>Code Quality Intelligence Agent</strong></p>
            </body>
            </html>
            """

            return await self.send_email(
                to_email=to_email,
                subject=subject,
                body=body,
                html_body=html_body
            )

        except Exception as e:
            logger.error(f"Weekly digest email failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'to_email': to_email
            }

    async def check_health(self) -> bool:
        """
        Check if email service is healthy.
        """
        try:
            # Test SMTP connection
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.smtp_username, self.smtp_password)
            server.quit()
            return True
        except Exception:
            return False
