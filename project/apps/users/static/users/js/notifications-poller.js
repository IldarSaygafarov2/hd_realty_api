/**
 * Опроc непрочитанных уведомлений в админке без перезагрузки.
 * Обновляет бейдж у ссылки «Уведомления» и показывает toast при новых.
 */
(function () {
    const POLL_INTERVAL_MS = 10000;
    const API_URL = "/api/admin/notifications/unread";
    const LINK_SELECTOR = 'a[href*="notification"]';

    let lastCount = 0;
    let badgeEl = null;

    function createBadge(count) {
        const el = document.createElement("span");
        el.className = "ms-2 inline-flex items-center justify-center min-w-[1.25rem] h-5 px-1.5 text-xs font-medium rounded-full bg-primary-500 text-white";
        el.setAttribute("data-notifications-badge", "true");
        el.textContent = count > 99 ? "99+" : String(count);
        return el;
    }

    function updateBadge(count) {
        const link = document.querySelector(LINK_SELECTOR);
        if (!link) return;
        if (badgeEl && badgeEl.parentNode) badgeEl.remove();
        if (count > 0) {
            badgeEl = createBadge(count);
            link.appendChild(badgeEl);
        }
        lastCount = count;
    }

    function showToast(title, message) {
        var container = document.getElementById("notifications-toast-container");
        if (!container) {
            container = document.createElement("div");
            container.id = "notifications-toast-container";
            container.className = "fixed top-4 right-4 z-[9999] space-y-2";
            document.body.appendChild(container);
        }
        var toast = document.createElement("div");
        toast.className = "px-4 py-3 rounded-lg shadow-lg bg-gray-800 text-white text-sm max-w-sm";
        toast.innerHTML = "<strong>" + (title || "") + "</strong><br>" + (message || "");
        container.appendChild(toast);
        setTimeout(function () {
            toast.remove();
        }, 5000);
    }

    function onNewNotifications(data) {
        var count = data.count || 0;
        var items = data.items || [];
        if (count > lastCount && items.length > 0) {
            var newOnes = items.slice(0, count - lastCount);
            newOnes.forEach(function (n) {
                showToast(n.title, n.message);
            });
        }
        updateBadge(count);
    }

    function fetchNotifications() {
        fetch(API_URL, { credentials: "same-origin" })
            .then(function (r) {
                if (r.status === 401) return null;
                return r.json();
            })
            .then(function (data) {
                if (data) onNewNotifications(data);
            })
            .catch(function () {});
    }

    function init() {
        var isAdmin = document.querySelector("#nav-sidebar-apps") ||
            document.querySelector(".layout-wrapper") ||
            document.querySelector(".unfold");
        if (!isAdmin && !/\/admin\//.test(window.location.pathname)) return;
        fetchNotifications();
        setInterval(fetchNotifications, POLL_INTERVAL_MS);
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", init);
    } else {
        init();
    }
})();
