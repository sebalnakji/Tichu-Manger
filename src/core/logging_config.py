"""
로깅 설정 초기화
logging.yaml 파일 기반으로 로거 구성
"""
import logging
import logging.config
import yaml
from pathlib import Path

from core.properties import settings


def setup_logging():
    """
    로깅 설정 초기화
    - logging.yaml 파일 로드
    - logs 디렉토리 자동 생성
    """
    # logs 디렉토리 생성
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    # logging.yaml 파일 경로 (src 폴더 기준 상위 폴더)
    config_path = Path(__file__).parent.parent.parent / "logging.yaml"

    if config_path.exists():
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f.read())
            logging.config.dictConfig(config)
    else:
        # yaml 파일이 없으면 기본 설정 사용
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s: %(levelname)s >> [%(name)s] %(message)s'
        )
        logging.warning(f"로깅 설정 파일을 찾을 수 없습니다: {config_path}")


def get_logger(name: str) -> logging.Logger:
    """
    모듈별 로거 반환

    Args:
        name: 로거 이름 (보통 __name__ 사용)

    Returns:
        logging.Logger: 설정된 로거 객체

    Example:
        logger = get_logger(__name__)
        logger.info("서버 시작")
    """
    return logging.getLogger(name)