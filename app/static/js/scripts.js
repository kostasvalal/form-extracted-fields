document.addEventListener("DOMContentLoaded", function() {
    const dropZone = document.getElementById("drop-zone");
    const fileInput = document.getElementById("file-input");
    const uploadButton = document.getElementById("upload-button");
    const downloadButton = document.getElementById("download-button");
    const newUploadButton = document.getElementById("new-upload-button");
    const message = document.getElementById("message");
    const form = document.getElementById("upload-form");
    let files = [];

    dropZone.addEventListener("dragover", (event) => {
        event.preventDefault();
        dropZone.classList.add("dragover");
    });

    dropZone.addEventListener("dragleave", () => {
        dropZone.classList.remove("dragover");
    });

    dropZone.addEventListener("drop", (event) => {
        event.preventDefault();
        dropZone.classList.remove("dragover");
        files = Array.from(event.dataTransfer.files);
        fileInput.files = new DataTransfer().files; // Clear file input
        updateFileList();
    });

    fileInput.addEventListener("change", (event) => {
        files = Array.from(event.target.files);
        updateFileList();
    });

    function updateFileList() {
        message.textContent = `${files.length} file(s) ready to upload.`;
    }

    form.addEventListener("submit", async (event) => {
        event.preventDefault();

        const formData = new FormData();
        files.forEach(file => {
            formData.append("files[]", file);
        });

        const selectedSampleFiles = Array.from(document.querySelectorAll('input[name="sample_files"]:checked'))
            .map(input => input.value);

        selectedSampleFiles.forEach(fileName => {
            formData.append("sample_files[]", fileName);
        });

        if (formData.getAll("files[]").length === 0 && formData.getAll("sample_files[]").length === 0) {
            alert("Please select files to upload.");
            return;
        }

        uploadButton.disabled = true;
        message.textContent = "Processing...";

        try {
            const response = await fetch("/upload", {
                method: "POST",
                body: formData
            });

            const result = await response.json();
            if (response.ok) {
                message.textContent = "Files uploaded successfully. Processing...";
                setTimeout(async () => {
                    const downloadResponse = await fetch(result.downloadUrl);
                    const downloadResult = await downloadResponse.json();
                    if (downloadResponse.ok) {
                        message.textContent = "Processing complete. Click Download to get your file.";
                        downloadButton.dataset.url = downloadResult.file_url;
                        downloadButton.disabled = false;
                        newUploadButton.disabled = false;
                    } else {
                        message.textContent = downloadResult.error;
                        uploadButton.disabled = false;
                    }
                }, 2000); // Simulate processing delay
            } else {
                message.textContent = result.error;
                uploadButton.disabled = false;
            }
        } catch (error) {
            message.textContent = `Error: ${error.message}`;
            uploadButton.disabled = false;
        }
    });

    downloadButton.addEventListener("click", () => {
        const url = downloadButton.dataset.url;
        if (url) {
            window.location.href = url;
        }
    });

    newUploadButton.addEventListener("click", () => {
        fileInput.value = "";
        document.querySelectorAll('input[name="sample_files"]').forEach(input => input.checked = false);
        message.textContent = "";
        uploadButton.disabled = false;
        downloadButton.disabled = true;
        newUploadButton.disabled = true;
    });
});
