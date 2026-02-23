/**
 * 인증 관리 모듈
 * localStorage를 사용한 인증 상태 관리
 */

const AuthManager = {
    ACTIVITY_KEY: 'tichu_last_activity',
    TIMEOUT_MS: 5 * 60 * 60 * 1000, // 5시간

    /**
     * 인증 정보 저장
     */
    setAuth(role, playerId = null, playerName = null) {
        const authData = {
            role: role,
            playerId: playerId,
            playerName: playerName,
            timestamp: new Date().getTime()
        };
        localStorage.setItem('tichu_auth', JSON.stringify(authData));
        this.updateActivity();
    },

    /**
     * 인증 정보 조회
     */
    getAuth() {
        const authData = localStorage.getItem('tichu_auth');
        if (!authData) return null;

        try {
            return JSON.parse(authData);
        } catch (error) {
            console.error('인증 정보 파싱 실패:', error);
            return null;
        }
    },

    /**
     * 인증 여부 확인 (만료 시 자동 로그아웃)
     */
    isAuthenticated() {
        const auth = this.getAuth();
        if (!auth) return false;
        const last = parseInt(localStorage.getItem(this.ACTIVITY_KEY) || '0');
        if (last && Date.now() - last > this.TIMEOUT_MS) {
            this.logout();
            return false;
        }
        return true;
    },

    /**
     * 관리자 여부 확인
     */
    isAdmin() {
        const auth = this.getAuth();
        return auth && auth.role === 'admin';
    },

    /**
     * 로그아웃
     */
    logout() {
        localStorage.removeItem('tichu_auth');
        localStorage.removeItem('admin_code');
        localStorage.removeItem(this.ACTIVITY_KEY);
    },

    /**
     * 마지막 활동 시간 갱신
     */
    updateActivity() {
        localStorage.setItem(this.ACTIVITY_KEY, Date.now().toString());
    },

    /**
     * 비활동 만료 체크 — 만료 시 자동 로그아웃
     */
    checkExpiry() {
        if (!this.getAuth()) return;
        const last = parseInt(localStorage.getItem(this.ACTIVITY_KEY) || '0');
        if (last && Date.now() - last > this.TIMEOUT_MS) {
            this.logout();
            window.location.reload();
        }
    },

    /**
     * 활동 감지 + 주기적 만료 체크 시작
     */
    startActivityTracker() {
        this.checkExpiry();
        ['click', 'touchstart'].forEach(evt => {
            document.addEventListener(evt, () => {
                if (this.getAuth()) this.updateActivity();
            }, { passive: true });
        });
        setInterval(() => this.checkExpiry(), 60 * 1000);
    },

    /**
     * 관리자 코드 가져오기 (API 요청용)
     */
    getAdminCode() {
        return localStorage.getItem('admin_code') || '';
    },

    /**
     * 관리자 코드 저장 (인증 성공 시)
     */
    setAdminCode(code) {
        localStorage.setItem('admin_code', code);
    },

    /**
     * 인증 모달 표시
     */
    showAuthModal(onSuccess, onCancel) {
        const modal = document.getElementById('auth-modal');
        if (!modal) {
            console.error('인증 모달을 찾을 수 없습니다.');
            return;
        }

        // 취소 콜백 저장
        this._onCancel = onCancel || null;

        // 모달 표시
        modal.classList.remove('hidden');

        // 입력 필드 초기화
        const input = document.getElementById('auth-code-input');
        input.value = '';
        input.focus();

        // 확인 버튼 이벤트
        const confirmBtn = document.getElementById('auth-confirm-btn');
        const newConfirmBtn = confirmBtn.cloneNode(true);
        confirmBtn.parentNode.replaceChild(newConfirmBtn, confirmBtn);

        newConfirmBtn.addEventListener('click', async () => {
            await this.verifyCode(input.value, onSuccess);
        });

        // Enter 키 이벤트
        input.addEventListener('keypress', async (e) => {
            if (e.key === 'Enter') {
                await this.verifyCode(input.value, onSuccess);
            }
        });
    },

    /**
     * 인증 모달 닫기
     */
    closeAuthModal() {
        const modal = document.getElementById('auth-modal');
        if (modal) {
            modal.classList.add('hidden');
        }
        if (this._onCancel) {
            const cb = this._onCancel;
            this._onCancel = null;
            cb();
        }
    },

    /**
     * 코드 검증
     */
    async verifyCode(code, onSuccess) {
        // 공백 체크
        if (/\s/.test(code)) {
            this.showError('코드에는 공백을 포함할 수 없습니다.');
            return;
        }

        if (!code) {
            this.showError('코드를 입력해주세요.');
            return;
        }

        try {
            const response = await fetch('/api/auth/verify', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ code: code }),
            });

            if (!response.ok) {
                const error = await response.json();
                this.showError(error.detail || '코드가 일치하지 않습니다.');
                this.shakeModal();
                return;
            }

            const data = await response.json();
            this.setAuth(data.role, data.player_id, data.player_name);

            // 관리자 코드 저장 (관리자인 경우)
            if (data.role === 'admin') {
                this.setAdminCode(code);
            }

            this._onCancel = null;
            this.closeAuthModal();

            if (onSuccess) {
                onSuccess(data);
            }
        } catch (error) {
            console.error('인증 실패:', error);
            this.showError('인증 중 오류가 발생했습니다.');
        }
    },

    /**
     * 에러 메시지 표시
     */
    showError(message) {
        const errorDiv = document.getElementById('auth-error-message');
        if (errorDiv) {
            errorDiv.textContent = message;
            errorDiv.classList.remove('hidden');

            setTimeout(() => {
                errorDiv.classList.add('hidden');
            }, 3000);
        }
    },

    /**
     * 모달 흔들림 효과
     */
    shakeModal() {
        const modalContent = document.querySelector('#auth-modal > div');
        if (modalContent) {
            modalContent.classList.add('shake');
            setTimeout(() => {
                modalContent.classList.remove('shake');
            }, 500);
        }
    },

    /**
     * 공백 입력 방지
     */
    preventSpace(inputElement) {
        inputElement.addEventListener('keydown', (e) => {
            if (e.key === ' ' || e.code === 'Space') {
                e.preventDefault();
                this.showError('공백은 입력할 수 없습니다.');
            }
        });
    }
};

// 전역으로 노출
window.AuthManager = AuthManager;

// 페이지 로드 시 활동 트래커 시작
document.addEventListener('DOMContentLoaded', () => {
    AuthManager.startActivityTracker();
});