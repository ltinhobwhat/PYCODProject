// static/js/saves.js
document.addEventListener('DOMContentLoaded', function() {
    // Save game functionality
    document.getElementById('saveGameBtn').addEventListener('click', function() {
        document.getElementById('saveModal').style.display = 'block';
    });
    
    document.getElementById('confirmSave').addEventListener('click', function() {
        const saveName = document.getElementById('saveName').value || 'Autosave';
        
        fetch('/save', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: `save_name=${encodeURIComponent(saveName)}`
        })
        .then(response => response.json())
        .then(data => {
            if(data.status === 'success') {
                alert('Game saved successfully!');
                document.getElementById('saveModal').style.display = 'none';
                loadSaveList();
            }
        });
    });
    
    // Load save list
    function loadSaveList() {
        fetch('/list')
        .then(response => response.json())
        .then(saves => {
            const saveList = document.getElementById('saveList');
            saveList.innerHTML = '';
            
            saves.forEach(save => {
                const saveElement = document.createElement('div');
                saveElement.className = 'save-item';
                saveElement.innerHTML = `
                    <span>${save.name} (${save.date})</span>
                    <button onclick="loadGame(${save.id})">LOAD</button>
                `;
                saveList.appendChild(saveElement);
            });
        });
    }
    
    // Load game function
    window.loadGame = function(saveId) {
        fetch(`/load/${saveId}`)
        .then(response => response.json())
        .then(data => {
            if(data.status === 'success') {
                alert('Game loaded!');
                document.getElementById('saveModal').style.display = 'none';
                location.reload(); // Refresh to show loaded state
            }
        });
    }
    
    // Initial load of saves
    loadSaveList();
});