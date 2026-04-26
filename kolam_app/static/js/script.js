// static/js/symmetry_checker.js
const fileInput = document.getElementById("kolam_image");
const canvas = document.getElementById("output_canvas");
const ctx = canvas.getContext("2d");

const rotationSlider = document.getElementById("rotation_slider");
const rotationInput = document.getElementById("rotation_input");
const rotationValue = document.getElementById("rotation_value");

let uploadedImage = null;
let currentRotation = 0;

// --- Load and draw the uploaded image ---
fileInput.addEventListener("change", (e) => {
    const file = e.target.files[0];
    if (!file) return;
    const reader = new FileReader();

    reader.onload = function (event) {
        const img = new Image();
        img.onload = function () {
            uploadedImage = img;
            currentRotation = 0;
            drawImageRotated();
            document.getElementById("controls").style.display = "block";
        };
        img.src = event.target.result;
    };
    reader.readAsDataURL(file);
});

// --- Draw image with the current rotation ---
function drawImageRotated() {
    if (!uploadedImage) return;
    const w = canvas.width;
    const h = canvas.height;
    ctx.clearRect(0, 0, w, h);

    ctx.save();
    ctx.translate(w / 2, h / 2);
    ctx.rotate((currentRotation * Math.PI) / 180);
    ctx.drawImage(
        uploadedImage,
        -uploadedImage.width / 2,
        -uploadedImage.height / 2
    );
    ctx.restore();
}

// --- Slider & number box are linked ---
function updateRotation(val) {
    currentRotation = parseFloat(val) || 0;
    rotationSlider.value = currentRotation;
    rotationInput.value = currentRotation;
    rotationValue.textContent = `${currentRotation}°`;
    drawImageRotated();
}

rotationSlider.addEventListener("input", e => updateRotation(e.target.value));
rotationInput.addEventListener("input", e => updateRotation(e.target.value));
