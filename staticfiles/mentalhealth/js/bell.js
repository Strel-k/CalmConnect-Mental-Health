const bell = document.querySelector('.bx.bxs-bell');

bell.addEventListener('mouseenter', () => {
    bell.classList.add('bx-wiggle');

    // Remove the class after animation so it can re-trigger next time
    setTimeout(() => {
        bell.classList.remove('bx-wiggle');
    }, 1000); // Duration of the animation
});