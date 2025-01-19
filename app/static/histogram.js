/**
 * Processes an image to generate and display a histogram of its 3 color channels.
 *
 * @param {ImageData} inImg - The input image data to be processed, here, it is the user chosen image.
 */
function processImage(inImg) {
  const width = inImg.width;
  const height = inImg.height;

  // Create a 32-bit int array from the image data buffer
  const src = new Uint32Array(inImg.data.buffer);

  // Initialize histograms color and brightness arrays
  let histBrightness = new Array(256).fill(0);
  let histR = new Array(256).fill(0);
  let histG = new Array(256).fill(0);
  let histB = new Array(256).fill(0);

  // Iterate over each pixel
  for (let i = 0; i < src.length; i++) {
    // Extract the red, green, and blue components for this pixel
    let r = src[i] & 0xFF;
    let g = (src[i] >> 8) & 0xFF;
    let b = (src[i] >> 16) & 0xFF;

    // Update the brightness histogram
    histBrightness[r]++;
    histBrightness[g]++;
    histBrightness[b]++;

    // Update the individual color channel histograms
    histR[r]++;
    histG[g]++;
    histB[b]++;
  }

  // Determine the maximum value in the histograms for scaling
  let maxBrightness = 0;
  for (let i = 0; i < 256; i++) {
    if (maxBrightness < histR[i]) maxBrightness = histR[i];
    if (maxBrightness < histG[i]) maxBrightness = histG[i];
    if (maxBrightness < histB[i]) maxBrightness = histB[i];
  }

  const canvas = document.getElementById("canvas-histogram");
  const ctx = canvas.getContext("2d");

  let guideHeight = 8;
  let startY = canvas.height - guideHeight;

  // Calculate the width of each histogram bar and the scaling factor for the height
  let dx = canvas.width / 256;
  let dy = startY / maxBrightness;

  ctx.lineWidth = dx;
  ctx.fillStyle = "#fff";
  ctx.fillRect(0, 0, canvas.width, canvas.height);

  // Draw the histogram bars for each color channel
  for (let i = 0; i < 256; i++) {
    let x = i * dx;

    // Red channel
    ctx.strokeStyle = "rgba(220,0,0,0.5)";
    ctx.beginPath();
    ctx.moveTo(x, startY);
    ctx.lineTo(x, startY - histR[i] * dy);
    ctx.closePath();
    ctx.stroke();

    // Green channel
    ctx.strokeStyle = "rgba(0,210,0,0.5)";
    ctx.beginPath();
    ctx.moveTo(x, startY);
    ctx.lineTo(x, startY - histG[i] * dy);
    ctx.closePath();
    ctx.stroke();

    // Blue channel
    ctx.strokeStyle = "rgba(0,0,255,0.5)";
    ctx.beginPath();
    ctx.moveTo(x, startY);
    ctx.lineTo(x, startY - histB[i] * dy);
    ctx.closePath();
    ctx.stroke();

    // Guide line (at the bottom of the canvas for brightness)
    ctx.strokeStyle = "rgb(" + i + ", " + i + ", " + i + ")";
    ctx.beginPath();
    ctx.moveTo(x, startY);
    ctx.lineTo(x, canvas.height);
    ctx.closePath();
    ctx.stroke();
  }
}

/**
 * Retrieves the image data from an HTML image element, which is the user chosen image.
 *
 * @param {string} el - The ID of the image element.
 * @returns {ImageData} - The image data of the specified image element.
 */
function getImageData(el) {
  const canvas = document.createElement("canvas");
  const context = canvas.getContext("2d");

  const img = document.getElementById(el);

  // Set the canvas dimensions to match the image
  canvas.width = img.width;
  canvas.height = img.height;

  // Draw the image onto the canvas
  context.drawImage(img, 0, 0);

  // Return the image data from the canvas
  return context.getImageData(0, 0, img.width, img.height);
}

document.getElementById("submit-btn").addEventListener("click", function () {
  // Get selected image ID
  const select = document.getElementById("image_id");
  const selectedImage = select.value;

  // Set the source of the thumbnail image to the selected image
  const img = document.getElementById("img-thumbnail");
  img.src = "static/imagenet_subset/" + selectedImage;

  // Process the image data once the image has loaded
  img.onload = function () {
    const imageData = getImageData("img-thumbnail");
    processImage(imageData);
  };
});
