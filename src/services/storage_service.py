"""
Storage Service
Supabase Storage를 이용한 파일 업로드/삭제 관리
"""
import os
from typing import Optional
from datetime import datetime
from supabase import create_client, Client
from core.properties import settings
from core.logging_config import get_logger

logger = get_logger(__name__)


class StorageService:
    """Supabase Storage 서비스"""

    def __init__(self):
        """Supabase 클라이언트 초기화"""
        if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
            logger.warning("Supabase 설정이 없습니다. Storage 기능이 비활성화됩니다.")
            self.client: Optional[Client] = None
            self.bucket_name = settings.SUPABASE_BUCKET
        else:
            self.client: Client = create_client(
                settings.SUPABASE_URL,
                settings.SUPABASE_KEY
            )
            self.bucket_name = settings.SUPABASE_BUCKET
            logger.info(f"Supabase Storage 초기화 완료: {self.bucket_name}")

    def upload_profile_image(
            self,
            player_id: int,
            file_content: bytes,
            file_extension: str = "jpg"
    ) -> Optional[str]:
        """
        프로필 이미지 업로드

        Args:
            player_id: 플레이어 ID
            file_content: 이미지 파일 바이너리 데이터
            file_extension: 파일 확장자 (jpg, png 등)

        Returns:
            str: 업로드된 이미지의 Public URL 또는 None
        """
        if not self.client:
            logger.error("Supabase 클라이언트가 초기화되지 않았습니다.")
            return None

        try:
            # 파일명 생성: player_{id}_{timestamp}.{ext}
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            file_name = f"player_{player_id}_{timestamp}.{file_extension}"
            file_path = f"{file_name}"

            # Supabase Storage에 업로드
            response = self.client.storage.from_(self.bucket_name).upload(
                path=file_path,
                file=file_content,
                file_options={
                    "content-type": f"image/{file_extension}",
                    "upsert": "false"  # 중복 파일명 방지
                }
            )

            # Public URL 생성
            public_url = self.client.storage.from_(self.bucket_name).get_public_url(file_path)

            logger.info(f"프로필 이미지 업로드 성공: {file_path}")
            return public_url

        except Exception as e:
            logger.error(f"프로필 이미지 업로드 실패: {e}")
            return None

    def delete_profile_image(self, image_url: str) -> bool:
        """
        프로필 이미지 삭제

        Args:
            image_url: 삭제할 이미지의 Public URL

        Returns:
            bool: 삭제 성공 여부
        """
        if not self.client:
            logger.error("Supabase 클라이언트가 초기화되지 않았습니다.")
            return False

        try:
            # URL에서 파일명 추출
            # 예: https://xxx.supabase.co/storage/v1/object/public/tichu-profiles/player_1_20260219.jpg
            # → player_1_20260219.jpg
            file_path = image_url.split(f"/{self.bucket_name}/")[-1]

            # 기본 이미지는 삭제하지 않음
            if "default-profile" in file_path or not file_path.startswith("player_"):
                logger.info(f"기본 이미지는 삭제하지 않습니다: {file_path}")
                return True

            # Supabase Storage에서 삭제
            self.client.storage.from_(self.bucket_name).remove([file_path])

            logger.info(f"프로필 이미지 삭제 성공: {file_path}")
            return True

        except Exception as e:
            logger.error(f"프로필 이미지 삭제 실패: {e}")
            return False


# 전역 Storage 서비스 인스턴스
storage_service = StorageService()