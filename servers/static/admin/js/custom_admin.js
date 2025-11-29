(function() {
    'use strict';
    
    function addProjectInfo() {
        // Check if already added
        if (document.querySelector('.sidebar-project-info')) {
            return;
        }
        
        const sidebar = document.querySelector('.main-sidebar');
        if (!sidebar) {
            return;
        }
        
        // Create project info element
        const projectInfo = document.createElement('div');
        projectInfo.className = 'sidebar-project-info';
        projectInfo.innerHTML = `
            <a href="https://github.com/MoYuK1ng/MC_rcon_manage" target="_blank" rel="noopener noreferrer" title="MC RCON Manager on GitHub">
                <div class="project-icon">
                    <i class="fab fa-github"></i>
                </div>
                <div class="project-text">
                    <div class="project-name">MC RCON Manager</div>
                    <div class="project-link">
                        <i class="fas fa-external-link-alt"></i> View on GitHub
                    </div>
                </div>
            </a>
        `;
        
        // Append to sidebar
        sidebar.appendChild(projectInfo);
    }
    
    // Run when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', addProjectInfo);
    } else {
        addProjectInfo();
    }
    
    // Retry a few times to ensure it's added
    setTimeout(addProjectInfo, 100);
    setTimeout(addProjectInfo, 500);
    setTimeout(addProjectInfo, 1000);
})();
