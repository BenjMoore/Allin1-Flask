
document.addEventListener("DOMContentLoaded", function() {
    fetchFiles();

    // Upload form submission
    document.getElementById("uploadForm").addEventListener("submit", async function(event) {
        event.preventDefault();
        
        let formData = new FormData();
        let fileInput = document.getElementById("fileInput").files[0];
        let folderInput = document.getElementById("folderInput").value;

        if (!fileInput) {
            alert("Please select a file to upload.");
            return;
        }

        formData.append("file", fileInput);
        formData.append("folder", folderInput);

        let response = await fetch("/cloud/upload", {
            method: "POST",
            body: formData
        });

        let result = await response.json();
        alert(result.message);
        fetchFiles();  // Refresh the file list
    });
});

// Fetch files from the backend
async function fetchFiles() {
    let response = await fetch("/cloud/list");
    let files = await response.json();
    let fileList = document.getElementById("fileList");
    fileList.innerHTML = "";  // Clear previous entries

    if (files.error) {
        fileList.innerHTML = `<li>${files.error}</li>`;
        return;
    }

    files.forEach(file => {
        let listItem = document.createElement("li");
        listItem.innerHTML = `
            ${file.name} (${file.type})
            ${file.type === "file" ? `<a href="/cloud/download/${file.name}" download>Download</a>` : ""}
            <button onclick="deleteFile('${file.name}')">Delete</button>
        `;
        fileList.appendChild(listItem);
    });
}

// Delete a file
async function deleteFile(fileName) {
    let response = await fetch("/cloud/delete", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ path: fileName })
    });

    let result = await response.json();
    alert(result.message);
    fetchFiles();  // Refresh the file list
}
