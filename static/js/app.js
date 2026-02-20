/**
 * Tichu Manager - 공통 JavaScript
 * API 통신 및 유틸리티 함수
 */

// API Base URL
const API_BASE_URL = '/api';

/**
 * API 요청 헬퍼 함수
 */
const api = {
    /**
     * GET 요청
     */
    async get(endpoint) {
        try {
            const response = await fetch(`${API_BASE_URL}${endpoint}`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return await response.json();
        } catch (error) {
            console.error(`GET ${endpoint} 실패:`, error);
            throw error;
        }
    },

    /**
     * POST 요청
     */
    async post(endpoint, data) {
        try {
            const response = await fetch(`${API_BASE_URL}${endpoint}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data),
            });
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
            }
            return await response.json();
        } catch (error) {
            console.error(`POST ${endpoint} 실패:`, error);
            throw error;
        }
    },

    /**
     * PUT 요청
     */
    async put(endpoint, data) {
        try {
            const response = await fetch(`${API_BASE_URL}${endpoint}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data),
            });
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
            }
            return await response.json();
        } catch (error) {
            console.error(`PUT ${endpoint} 실패:`, error);
            throw error;
        }
    },

    /**
     * DELETE 요청
     */
    async delete(endpoint) {
        try {
            const response = await fetch(`${API_BASE_URL}${endpoint}`, {
                method: 'DELETE',
            });
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return true;
        } catch (error) {
            console.error(`DELETE ${endpoint} 실패:`, error);
            throw error;
        }
    },
};

/**
 * 유틸리티 함수
 */
const utils = {
    /**
     * 로딩 스피너 표시
     */
    showLoading(elementId) {
        const element = document.getElementById(elementId);
        if (element) {
            element.innerHTML = '<div class="spinner"></div>';
        }
    },

    /**
     * 에러 메시지 표시
     */
    showError(message) {
        alert(message);
    },

    /**
     * 성공 메시지 표시
     */
    showSuccess(message) {
        // 간단한 토스트 메시지 (추후 개선 가능)
        const toast = document.createElement('div');
        toast.className = 'fixed top-4 right-4 bg-green-600 text-white px-6 py-3 rounded-lg shadow-lg z-50';
        toast.textContent = message;
        document.body.appendChild(toast);

        setTimeout(() => {
            toast.remove();
        }, 3000);
    },

    /**
     * 날짜 포맷팅 (YYYY-MM-DD)
     */
    formatDate(date) {
        const d = new Date(date);
        const year = d.getFullYear();
        const month = String(d.getMonth() + 1).padStart(2, '0');
        const day = String(d.getDate()).padStart(2, '0');
        return `${year}-${month}-${day}`;
    },

    /**
     * 숫자 포맷팅 (천 단위 콤마)
     */
    formatNumber(num) {
        return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
    },

    /**
     * 퍼센트 포맷팅
     */
    formatPercent(value, decimals = 1) {
        return value.toFixed(decimals) + '%';
    },

    /**
     * 디바운스 함수
     */
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },

    /**
     * 로컬 스토리지 저장
     */
    saveToStorage(key, value) {
        try {
            localStorage.setItem(key, JSON.stringify(value));
        } catch (error) {
            console.error('로컬 스토리지 저장 실패:', error);
        }
    },

    /**
     * 로컬 스토리지 불러오기
     */
    loadFromStorage(key) {
        try {
            const item = localStorage.getItem(key);
            return item ? JSON.parse(item) : null;
        } catch (error) {
            console.error('로컬 스토리지 로드 실패:', error);
            return null;
        }
    },
};

/**
 * 전역 에러 핸들러
 */
window.addEventListener('error', (event) => {
    console.error('전역 에러:', event.error);
});

window.addEventListener('unhandledrejection', (event) => {
    console.error('처리되지 않은 Promise 에러:', event.reason);
});

/**
 * 페이지 로드 완료 시 초기화
 */
document.addEventListener('DOMContentLoaded', () => {
    console.log('Tichu Manager 초기화 완료');
});