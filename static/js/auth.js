/**
 * 인증 관리 모듈
 * localStorage를 사용한 인증 상태 관리
 */

const AuthManager = {
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
     * 인증 여부 확인
     */
    isAuthenticated() {
        return this.getAuth() !== null;
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
    showAuthModal(onSuccess) {
        const modal = document.getElementById('auth-modal');
        if (!modal) {
            console.error('인증 모달을 찾을 수 없습니다.');
            return;
        }

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