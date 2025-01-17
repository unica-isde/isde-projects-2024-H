function processImage(inImg) {
  const width = inImg.width;
  const height = inImg.height;
  const src = new Uint32Array(inImg.data.buffer);

  let histBrightness = new Array(256).fill(0);
  let histR = new Array(256).fill(0);
  let histG = new Array(256).fill(0);
  let histB = new Array(256).fill(0);
  for (let i = 0; i < src.length; i++) {
    let r = src[i] & 0xFF;
    let g = (src[i] >> 8) & 0xFF;
    let b = (src[i] >> 16) & 0xFF;
    histBrightness[r]++;
    histBrightness[g]++;
    histBrightness[b]++;
    histR[r]++;
    histG[g]++;
    histB[b]++;
  }

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
  let dx = canvas.width / 256;
  let dy = startY / maxBrightness;
  ctx.lineWidth = dx;
  ctx.fillStyle = "#fff";
  ctx.fillRect(0, 0, canvas.width, canvas.height);

  for (let i = 0; i < 256; i++) {
    let x = i * dx;

    // Red
    ctx.strokeStyle = "rgba(220,0,0,0.5)";
    ctx.beginPath();
    ctx.moveTo(x, startY);
    ctx.lineTo(x, startY - histR[i] * dy);
    ctx.closePath();
    ctx.stroke();

    // Green
    ctx.strokeStyle = "rgba(0,210,0,0.5)";
    ctx.beginPath();
    ctx.moveTo(x, startY);
    ctx.lineTo(x, startY - histG[i] * dy);
    ctx.closePath();
    ctx.stroke();

    // Blue
    ctx.strokeStyle = "rgba(0,0,255,0.5)";
    ctx.beginPath();
    ctx.moveTo(x, startY);
    ctx.lineTo(x, startY - histB[i] * dy);
    ctx.closePath();
    ctx.stroke();

    // Guide
    ctx.strokeStyle = "rgb(" + i + ", " + i + ", " + i + ")";
    ctx.beginPath();
    ctx.moveTo(x, startY);
    ctx.lineTo(x, canvas.height);
    ctx.closePath();
    ctx.stroke();
  }
}

function getImageData(el) {
  const canvas = document.createElement("canvas");
  const context = canvas.getContext("2d");
  const img = document.getElementById(el);
  canvas.width = img.width;
  canvas.height = img.height;
  context.drawImage(img, 0, 0);
  return context.getImageData(0, 0, img.width, img.height);
}

document.getElementById("submit-btn").addEventListener("click", function () {
  const select = document.getElementById("image_id");
  const selectedImage = select.value;

  const img = document.getElementById("img-thumbnail");
  img.src = "static/imagenet_subset/" + selectedImage;

  img.onload = function () {
      const imageData = getImageData("img-thumbnail");
        processImage(imageData);
  };
});
