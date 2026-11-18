// Chronicle Application Scripts
document.addEventListener('DOMContentLoaded', function () {
    // 1. Auto-dismiss flash alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(function (alert) {
        setTimeout(function () {
            const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
            if (bsAlert) {
                bsAlert.close();
            }
        }, 5000);
    });

    // 2. Initialize Bootstrap tooltips if any
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // 3. Reading progress indicator on blog detail page
    const article = document.querySelector('.article-content');
    if (article) {
        const progressBar = document.createElement('div');
        progressBar.style.position = 'fixed';
        progressBar.style.top = '0';
        progressBar.style.left = '0';
        progressBar.style.height = '3px';
        progressBar.style.backgroundColor = '#4f46e5';
        progressBar.style.width = '0%';
        progressBar.style.zIndex = '9999';
        progressBar.style.transition = 'width 0.1s ease';
        document.body.appendChild(progressBar);

        window.addEventListener('scroll', function () {
            const articleRect = article.getBoundingClientRect();
            const articleTop = articleRect.top + window.scrollY;
            const articleHeight = articleRect.height;
            const scrollPos = window.scrollY;
            const windowHeight = window.innerHeight;

            if (scrollPos > articleTop) {
                const totalScrollable = articleHeight - windowHeight + 200;
                const progress = Math.min(100, Math.max(0, ((scrollPos - articleTop) / totalScrollable) * 100));
                progressBar.style.width = progress + '%';
            } else {
                progressBar.style.width = '0%';
            }
        });
    }
});
