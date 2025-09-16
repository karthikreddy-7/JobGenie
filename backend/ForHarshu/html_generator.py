import logging
from typing import List, Dict
from datetime import datetime

logger = logging.getLogger(__name__)


def generate_jobs_html(jobs_data: List[Dict]) -> str:
    """
    Generates a clean, minimalistic HTML table for a list of job data.
    """
    if not jobs_data:
        return "<p>No new job recommendations at this time. Stay tuned!</p>"

    # Style definitions for a modern look
    table_style = "width:100%; border-collapse: collapse; font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;"
    th_style = "padding: 16px; border-bottom: 2px solid #eaeaea; text-align: left; color: #666; font-weight: 500; font-size: 14px;"
    td_style = "padding: 16px; border-bottom: 1px solid #eaeaea; color: #333; font-size: 14px; vertical-align: middle;"
    tr_hover_script = "this.style.backgroundColor='#f9f9f9';"
    tr_unhover_script = "this.style.backgroundColor='white';"

    # Enhanced button styles for better UI
    button_style_primary = "display: inline-block; text-decoration: none; padding: 10px 18px; border-radius: 6px; color: #fff; background-color: #007bff; font-weight: 500; border: 0; box-shadow: 0 1px 3px rgba(0,0,0,0.1);"
    button_style_secondary = "display: inline-block; text-decoration: none; padding: 9px 18px; border-radius: 6px; color: #333; background-color: #f0f0f0; font-weight: 500; border: 1px solid #ddd; margin-right: 8px;"

    # Hover effects for buttons (using JS for email client compatibility)
    primary_hover_on = "this.style.backgroundColor='#0056b3'"
    primary_hover_off = "this.style.backgroundColor='#007bff'"
    secondary_hover_on = "this.style.backgroundColor='#e0e0e0'"
    secondary_hover_off = "this.style.backgroundColor='#f0f0f0'"

    html = f'<table style="{table_style}">'
    html += """
        <thead>
            <tr>
                <th style="{th_style}">Job Title</th>
                <th style="{th_style}">Company</th>
                <th style="{th_style}">Location</th>
                <th style="{th_style}">Experience</th>
                <th style="{th_style}">Match Score</th>
                <th style="{th_style}">Links</th>
            </tr>
        </thead>
        <tbody>
    """.format(th_style=th_style)

    for job in jobs_data:
        job_url_direct = job.get("job_url_direct")
        html += f"""
            <tr onmouseover="{tr_hover_script}" onmouseout="{tr_unhover_script}" style="background-color: white; transition: background-color 0.2s ease;">
                <td style="{td_style} word-wrap: break-word; max-width: 300px; font-weight: 600; color: #0056b3;">{job['title']}</td>
                <td style="{td_style} word-wrap: break-word;">{job['company']}</td>
                <td style="{td_style}">{job.get('location', 'N/A')}</td>
                <td style="{td_style} text-align: center;">{job.get('min_exp_required', 'N/A')} Year/s</td>
                <td style="{td_style} text-align: center; font-weight: 600;">{job['score']:.2f}</td>
                <td style="{td_style} min-width: 220px;">
                    <a href="{job['job_url']}" style="{button_style_secondary}" onmouseover="{secondary_hover_on}" onmouseout="{secondary_hover_off}">View Job</a>
                    {f'<a href="{job_url_direct}" style="{button_style_primary}" onmouseover="{primary_hover_on}" onmouseout="{primary_hover_off}">Apply Now</a>' if job_url_direct else ''}
                </td>
            </tr>
        """
    html += "</tbody></table>"
    return html


def wrap_html_body(content: str, user_name: str = "there") -> str:
    """
    Wraps the provided HTML content in a full, styled HTML body for emails.
    """
    full_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Your Job Recommendations</title>
    </head>
    <body style="font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; font-size: 16px; line-height: 1.6; color: #333; margin: 0; padding: 0; background-color: #f4f4f4;">
        <div style="max-width: 950px; margin: 20px auto; padding: 30px; background-color: #ffffff; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
            <div style="border-bottom: 2px solid #eaeaea; padding-bottom: 20px; margin-bottom: 30px;">
                 <h1 style="font-size: 24px; color: #333; margin: 0;">JobGenie</h1>
                 <p style="font-size: 16px; color: #666; margin: 5px 0 0;">Your Personal Job Curator</p>
            </div>
            <p style="margin-bottom: 25px;">Hi {user_name},</p>
            <p style="margin-bottom: 25px;">Here are your latest job recommendations, tailored just for you. We've found some exciting new opportunities that match your profile.</p>
            {content}
            <p style="margin-top: 30px;">Good luck with your applications!</p>
            <p>Best regards,<br><strong>The JobGenie Team</strong></p>
            <div style="border-top: 2px solid #eaeaea; padding-top: 20px; margin-top: 30px; font-size: 12px; color: #999; text-align: center;">
                <p>You received this email because you are subscribed to JobGenie. You can manage your preferences in your account settings.</p>
                <p>&copy; {datetime.now().year} JobGenie. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """
    return full_html

