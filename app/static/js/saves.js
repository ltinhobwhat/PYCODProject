// static/js/saves.js
document.addEventListener('DOMContentLoaded', function() {
    const saveBtn = document.getElementById('saveGameBtn');
    const modal = document.getElementById('saveModal');
    const confirmBtn = document.getElementById('confirmSave');
    const saveNameInput = document.getElementById('saveName');
    const saveStatus = document.getElementById('saveStatus');
    
    // Save game functionality
    saveBtn.addEventListener('click', function() {
        modal.style.display = 'block';
    });
    
    confirmBtn.addEventListener('click', function() {
        const saveName = saveNameInput.value || 'Autosave';
        saveStatus.textContent = "Saving game...";
        
        fetch('/saves/save', {  // Fixed endpoint
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: `save_name=${encodeURIComponent(saveName)}`
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            if(data.status === 'success') {
                saveStatus.textContent = "✅ Game saved successfully!";
                setTimeout(() => {
                    modal.style.display = 'none';
                    saveStatus.textContent = "";
                }, 2000);
                loadSaveList(); // Refresh the save list
            } else {
                throw new Error(data.message || 'Unknown error from server');
            }
        })
        .catch(error => {
            console.error('Save error:', error);
            saveStatus.textContent = `❌ Error: ${error.message}`;
        });
    });
    
    // Load save list
    function loadSaveList() {
        fetch('/saves/list')  // Fixed endpoint
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(saves => {
            const saveList = document.getElementById('saveList');
            if (!saveList) return;
            
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
        })
        .catch(error => {
            console.error('Error loading saves:', error);
        });
    }
    
    // Load game function
    window.loadGame = function(saveId) {
        fetch(`/saves/load/${saveId}`)  // Fixed endpoint
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            if(data.status === 'success') {
                alert('Game loaded!');
                document.getElementById('saveModal').style.display = 'none';
                location.reload(); // Refresh to show loaded state
            } else {
                throw new Error(data.message || 'Unknown error loading game');
            }
        })
        .catch(error => {
            console.error('Load error:', error);
            alert(`Error loading game: ${error.message}`);
        });
    }
    
    // Initial load of saves
    loadSaveList();
});