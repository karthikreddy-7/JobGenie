import logging
from typing import List, Dict

logger = logging.getLogger(__name__)

def generate_jobs_html(jobs_data: List[Dict]) -> str:
    if not jobs_data:
        return "<p>No new job recommendations at this time.</p>"

    html = """
    <table style="width:100%; border-collapse: collapse; font-family: Arial, sans-serif; font-size: 14px;">
        <thead>
            <tr>
                <th style="padding: 10px; border-bottom: 1px solid #ccc; text-align: left;">Job Title</th>
                <th style="padding: 10px; border-bottom: 1px solid #ccc; text-align: left;">Company</th>
                <th style="padding: 10px; border-bottom: 1px solid #ccc; text-align: left;">Location</th>
                <th style="padding: 10px; border-bottom: 1px solid #ccc; text-align: left;">Min Exp Required</th>
                <th style="padding: 10px; border-bottom: 1px solid #ccc; text-align: left;">Date Posted</th>
                <th style="padding: 10px; border-bottom: 1px solid #ccc; text-align: left;">Match Score</th>
                <th style="padding: 10px; border-bottom: 1px solid #ccc; text-align: left;">Job Links</th>
            </tr>
        </thead>
        <tbody>
    """
    for job in jobs_data:
        html += f"""
            <tr>
                <td style="padding: 8px; border-bottom: 1px solid #eee;">{job['title']}</td>
                <td style="padding: 8px; border-bottom: 1px solid #eee;">{job['company']}</td>
                <td style="padding: 8px; border-bottom: 1px solid #eee;">{job.get('location', 'N/A')}</td>
                <td style="padding: 8px; border-bottom: 1px solid #eee;">{job.get('min_exp_required', 'N/A')}</td>
                <td style="padding: 8px; border-bottom: 1px solid #eee;">{job.get('date_posted', 'N/A')}</td>
                <td style="padding: 8px; border-bottom: 1px solid #eee;">{job['score']:.2f}</td>
                <td style="padding: 8px; border-bottom: 1px solid #eee;">
                    <a href="{job['job_url']}" style="text-decoration:none; padding:4px 8px; border:1px solid #333; border-radius:3px; color:#333; margin-right:4px;">Job Page</a>
                    {f'<a href="{job.get("job_url_direct")}" style="text-decoration:none; padding:4px 8px; border:1px solid #333; border-radius:3px; color:#333;">Apply Directly</a>' if job.get("job_url_direct") else ''}
                </td>
            </tr>
        """
    html += "</tbody></table>"
    return html


def wrap_html_body(content: str) -> str:
    full_html = f"""
    <html>
        <body style="font-family: Arial, sans-serif; font-size: 14px; line-height: 1.5; color: #333; margin:0; padding:0;">
            <div style="max-width: 700px; margin: 20px auto; padding: 20px;">
                <p>Hi there,</p>
                <p>Here are your latest job recommendations:</p>
                {content}
                <p>Good luck with your applications!</p>
                <p>Best regards,<br><strong>Your JobGenie Team</strong></p>
            </div>
        </body>
    </html>
    """
    return full_html
