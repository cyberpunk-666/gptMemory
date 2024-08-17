let currentEditId = null;
let newMemoryEditor;
let editMemoryEditor;
let allMemories = [];

function initEditors() {
    newMemoryEditor = ace.edit("newMemoryEditor");
    newMemoryEditor.setTheme("ace/theme/github");
    newMemoryEditor.session.setMode("ace/mode/json");

    editMemoryEditor = ace.edit("editMemoryEditor");
    editMemoryEditor.setTheme("ace/theme/github");
    editMemoryEditor.session.setMode("ace/mode/json");
}

function fetchMemories() {
    fetch('/retrieve-memory')
        .then(response => response.json())
        .then(data => {
            allMemories = data;  // Save all memories for filtering
            displayMemories(data);
        });
}

function displayMemories(memories) {
    const tableBody = document.getElementById('memoryTable').getElementsByTagName('tbody')[0];
    tableBody.innerHTML = '';
    memories.forEach(memory => {
        const formattedDate = formatDate(memory.memory_data.date);
        const row = tableBody.insertRow();
        row.insertCell(0).innerHTML = memory.id;
        row.insertCell(1).innerHTML = formattedDate || 'N/A';
        row.insertCell(2).innerHTML = memory.memory_data.title || 'N/A';
        row.insertCell(3).innerHTML = memory.memory_data.content || 'N/A';
        const actionsCell = row.insertCell(4);
        actionsCell.innerHTML = `
            <button onclick="openEditModal(${memory.id})">Edit</button>
            <button onclick="deleteMemory(${memory.id})">Delete</button>
        `;
    });
}

function formatDate(isoDate) {
    if (!isoDate) return 'N/A';
    const date = new Date(isoDate);
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');
    const seconds = String(date.getSeconds()).padStart(2, '0');
    return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;
}

function filterMemories() {
    const filterTitle = document.getElementById('filterTitle').value.toLowerCase();
    const filterDate = document.getElementById('filterDate').value;
    const filteredMemories = allMemories.filter(memory => {
        const titleMatch = memory.memory_data.title.toLowerCase().includes(filterTitle);
        const dateMatch = filterDate ? memory.memory_data.date === filterDate : true;
        return titleMatch && dateMatch;
    });
    displayMemories(filteredMemories);
}

function openAddModal() {
    newMemoryEditor.setValue('', -1); // Start with an empty template
    document.getElementById('newMemoryTitle').value = '';
    document.getElementById('addModal').style.display = 'block';
}

function addMemory() {
    const title = document.getElementById('newMemoryTitle').value;
    const content = newMemoryEditor.getValue();
    const memoryData = {
        title: title,
        content: content
    };
    fetch('/store-memory', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ memory_data: memoryData })
    })
    .then(response => response.json())
    .then(data => {
        alert(data.message);
        fetchMemories();
        closeModal('addModal');
    });
}

function openEditModal(id) {
    currentEditId = id;
    const memory = allMemories.find(m => m.id === id);

    // Format the datetime string to fit the input field
    const formattedDate = memory.memory_data.date ? new Date(memory.memory_data.date).toISOString().slice(0, 16) : '';

    document.getElementById('editMemoryDate').value = formattedDate;
    document.getElementById('editMemoryTitle').value = memory.memory_data.title || '';
    editMemoryEditor.setValue(memory.memory_data.content || '', -1);
    document.getElementById('editModal').style.display = 'block';
}

function saveMemory() {
    const title = document.getElementById('editMemoryTitle').value;
    const content = editMemoryEditor.getValue();
    const date = document.getElementById('editMemoryDate').value; // This will be in 'YYYY-MM-DDTHH:MM' format

    const memoryData = {
        id: currentEditId,
        memory_data: {
            date: date ? new Date(date).toISOString() : '', // Convert to ISO string
            title: title,
            content: content
        }
    };

    fetch('/modify-memory', {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(memoryData)
    })
    .then(response => response.json())
    .then(data => {
        alert(data.message);
        fetchMemories();
        closeModal('editModal');
    });
}

function deleteMemory(id) {
    if (confirm('Are you sure you want to delete this memory?')) {
        fetch('/delete-memory', {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ id: id })
        })
        .then(response => response.json())
        .then(data => {
            alert(data.message);
            fetchMemories();
        });
    }
}

function closeModal(modalId) {
    document.getElementById(modalId).style.display = 'none';
}

// Initialize Ace Editors on page load
window.onload = function() {
    initEditors();
    fetchMemories();
};

// Close the modal if the user clicks outside of it
window.onclick = function(event) {
    if (event.target.className.includes('modal')) {
        event.target.style.display = "none";
    }
}
