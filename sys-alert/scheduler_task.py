import schedule
import threading
import queue
import functools
import os
import datetime
import sys
import smtplib
import mimetypes
import re
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import Header
from email.utils import parseaddr, formataddr


class Mail(object):
    def __init__(self):
        self.smtp_server = "smtp.163.com"
        self.smtp_port = 25
        self.from_addr = "jinjiegingo@163.com"
        self.password = "GEUTLGCPMVBEHYNS"
        self.to_addr = ["jinjie@shukun.net", "jinjiegingo@163.com"]
        self.msg = MIMEMultipart()
        self.msg['From'] = self._format_addr('SHUKUNQA <%s>' % self.from_addr)
        self.msg['To'] = self._format_addr('Receiver <%s>' % self.to_addr[0])
        self.msg['Subject'] = Header('这是一封来自{}监控系统日志的测试的邮件...'.format(server_ip), 'utf-8').encode()

    @staticmethod
    def _format_addr(s):
        name, addr = parseaddr(s)
        return formataddr((Header(name, 'utf-8').encode(), addr))

    def with_annex(self, file_path):
        ctype, encoding = mimetypes.guess_type(file_path)
        if ctype is None or encoding is not None:
            ctype = 'application/octet-stream'
        maintype, subtype = ctype.split('/', 1)

        with open(file_path, 'rb') as f:
            mime = MIMEBase(maintype, subtype, filename=os.path.basename(file_path))
            mime.add_header('Content-Disposition', 'attachment', filename=os.path.basename(file_path))
            mime.add_header('Content-ID', '<0>')
            mime.add_header('X-Attachment-Id', '0')
            mime.set_payload(f.read())
            encoders.encode_base64(mime)
            # 添加到MIMEMultipart:
            self.msg.attach(mime)

    def send_mail(self, email_body):
        server = smtplib.SMTP(self.smtp_server, self.smtp_port)
        server.starttls()
        # 邮件正文是MIMEText:
        self.msg.attach(MIMEText(email_body, 'plain', 'utf-8'))
        server.set_debuglevel(1)
        server.login(self.from_addr, self.password)
        server.sendmail(self.from_addr, self.to_addr, self.msg.as_string())
        server.quit()


log_folder = os.getenv("log_folder", "/opt/log")
log_names = os.getenv("log_names", ["kern.log", "test.log"])
kern_keywords = os.getenv("kern_keywords", ["error", "exception", "docker"])
_job_queue = queue.Queue()
interval_time = int(os.getenv("interval_time", 60))

if not isinstance(kern_keywords, list):
    kern_keywords = kern_keywords.split(",")

if not isinstance(log_names, list):
    kern_keywords = log_names.split(",")

server_ip = os.getenv("server_ip")
if not server_ip and sys.platform != "darwin":
    print("please edit the docker-compose.yaml and  add server ip env")
    sys.exit()

print("init monitor ")
print("log_folder {} \n"
      "log_names {} \n"
      "kern_keywords {} \n"
      "interval_time {} \n"
      "server_ip {} \n".format(log_folder, str(log_names), str(kern_keywords), str(interval_time), str(server_ip)))


def find_keywords_job(key_args):
    message_list = list()
    interval_time_end = datetime.datetime.now() + (datetime.timedelta(seconds=(interval_time*(-1) + 1)))
    print("interval_time_end:", interval_time_end)
    for log_name in log_names:
        log_path = os.path.join(log_folder, log_name)
        if not os.path.exists(log_path):
            continue
        with open(log_path) as f:
            try:
                for message in reversed(f.readlines()):
                    # 由于是倒叙进行搜索文本，正则匹配到时间小于interval_time_end，break
                    message_time = re.findall(r".*\d\d:\d\d:\d\d", message)[0]
                    print("filter message: ", message_time)
                    message_time = datetime.datetime.strptime(
                        str(datetime.datetime.now().year) + message_time, "%Y%b %d %H:%M:%S")
                    if message_time <= interval_time_end:
                        print("日志内容时间 {} 小于间隔查询最大时间{}".format(message_time, interval_time_end))
                        break
                    for k in key_args:
                        if k.lower() in message.lower():
                            print("find key news {}".format(message))
                            message_list.append(message)
            except Exception as e:
                print(e)
            else:
                if message_list:
                    print("send mail ..")
                    mail = Mail()
                    mail.send_mail(email_body="\n".join(message_list))


def work_jobs():
    while True:
        job = _job_queue.get()
        job()


def schedule_task():
    schedule.every(interval_time).seconds.do(_job_queue.put, functools.partial(find_keywords_job, kern_keywords))
    worker_thread = threading.Thread(target=work_jobs)
    worker_thread.start()
    while True:
        schedule.run_pending()


if __name__ == '__main__':
    schedule_task()