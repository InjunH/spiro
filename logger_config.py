import logging
from logging.handlers import TimedRotatingFileHandler

def setup_logger():
    logger = logging.getLogger(__name__)
    if not logger.handlers:
        # 로거 생성
        logger.setLevel(logging.INFO)

        # TimedRotatingFileHandler 설정
        handler = TimedRotatingFileHandler('app.log', when='midnight', interval=1, backupCount=30)
        handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        logger.addHandler(handler)

        # StreamHandler 설정 (콘솔 출력을 위한 핸들러)
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        logger.addHandler(console_handler)

    return logger
