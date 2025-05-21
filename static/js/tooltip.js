document.addEventListener('click', function (e) {
const allTooltips = document.querySelectorAll('.tooltip');
allTooltips.forEach(t => t.classList.remove('active-tooltip'));

const tooltip = e.target.closest('.tooltip');
if (tooltip) {
    tooltip.classList.add('active-tooltip');
}
});