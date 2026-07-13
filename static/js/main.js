document.addEventListener('DOMContentLoaded', () => {
    const body = document.body;
    const toggleButton = document.querySelector('.nav-toggle');
    const closeButton = document.querySelector('[data-mobile-nav-close]');
    const backdrop = document.querySelector('[data-mobile-nav-backdrop]');
    const mobileNav = document.getElementById('mobile-nav');

    if (!toggleButton || !closeButton || !backdrop || !mobileNav) {
        return;
    }

    const openNav = () => {
        body.classList.add('mobile-nav-open');
        mobileNav.setAttribute('aria-hidden', 'false');
        toggleButton.setAttribute('aria-expanded', 'true');
    };

    const closeNav = () => {
        body.classList.remove('mobile-nav-open');
        mobileNav.setAttribute('aria-hidden', 'true');
        toggleButton.setAttribute('aria-expanded', 'false');
    };

    toggleButton.addEventListener('click', () => {
        if (body.classList.contains('mobile-nav-open')) {
            closeNav();
        } else {
            openNav();
        }
    });

    closeButton.addEventListener('click', closeNav);
    backdrop.addEventListener('click', closeNav);

    mobileNav.querySelectorAll('a').forEach((link) => {
        link.addEventListener('click', closeNav);
    });

    document.addEventListener('keydown', (event) => {
        if (event.key === 'Escape') {
            closeNav();
        }
    });
});
