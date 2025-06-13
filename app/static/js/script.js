// Dark mode toggle
document.getElementById('dark-mode-toggle')?.addEventListener('click', async () => {
    try {
        const response = await fetch('/toggle_dark_mode', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            }
        });
        
        const data = await response.json();
        document.body.classList.toggle('dark-mode', data.dark_mode);
    } catch (error) {
        console.error('Error toggling dark mode:', error);
    }
});

// Task filtering
document.addEventListener('DOMContentLoaded', () => {
    const searchInput = document.getElementById('search-tasks');
    const categoryFilter = document.getElementById('category-filter');
    const taskItems = document.querySelectorAll('.task-item');
    
    if (searchInput) {
        searchInput.addEventListener('input', filterTasks);
    }
    
    if (categoryFilter) {
        categoryFilter.addEventListener('change', filterTasks);
    }
    
    function filterTasks() {
        const searchTerm = searchInput?.value.toLowerCase() || '';
        const category = categoryFilter?.value || 'all';
        
        taskItems.forEach(task => {
            const title = task.querySelector('h3').textContent.toLowerCase();
            const description = task.querySelector('.task-description')?.textContent.toLowerCase() || '';
            const categories = task.querySelector('.categories')?.textContent.toLowerCase() || '';
            const isVisible = 
                (title.includes(searchTerm) || 
                description.includes(searchTerm) || 
                categories.includes(searchTerm)) &&
                (category === 'all' || categories.includes(category));
            
            task.style.display = isVisible ? 'block' : 'none';
        });
    }
});