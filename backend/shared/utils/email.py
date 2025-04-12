from email.mime.multipart import MIMEMultipart
from typing import List, Optional, Any

import aiosmtplib


async def send_email(from_addr:str, password:str, to, cc:List[str] = None, bcc:Optional[List[str]]=None, subject:Optional[str]=None, attachments:List[Any]=None, host:str=None, host_port:int=None):
    smtp_client = aiosmtplib.SMTP(hostname=host, port=host_port)
    msg = MIMEMultipart()
    if attachments:
        for attachment in attachments:
            msg.attach(attachment)
    msg['From'] = from_addr
    msg['To'] = to
    if cc:
        msg['Cc'] = cc
    if bcc:
        msg['Bcc'] = bcc
    msg['Subject'] = subject
    async with smtp_client:
        print(from_addr, password)
        await smtp_client.ehlo()
        await smtp_client.login(from_addr, password)
        await smtp_client.send_message(msg)
    return None
