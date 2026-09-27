document.addEventListener("DOMContentLoaded", function () {
    let addButton = document.querySelector(".object-tools a"); // Find "Add Product" button
    if (addButton) {
        let uploadButton = document.createElement("a");
        uploadButton.href = "/admin/products/product/upload-excel/";
        uploadButton.innerText = "Upload Excel";
        uploadButton.classList = addButton.classList; // Copy styles
        uploadButton.style.backgroundColor = "#28a745"; // Green color
        uploadButton.style.marginLeft = "10px"; // Space between buttons
        addButton.parentNode.appendChild(uploadButton);
    }
});
