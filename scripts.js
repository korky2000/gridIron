const canvas = document.getElementById('gridCanvas');
const ctx = canvas.getContext('2d');
const gridSize = 20;
const cellSize = canvas.width / gridSize;
let circles = [];

function drawGrid() {
    ctx.clearRect(0, 0, canvas.width, canvas.height); // Clear canvas before redrawing
    for (let x = 0; x <= canvas.width; x += cellSize) {
        ctx.moveTo(x, 0);
        ctx.lineTo(x, canvas.height);
    }
    for (let y = 0; y <= canvas.height; y += cellSize) {
        ctx.moveTo(0, y);
        ctx.lineTo(canvas.width, y);
    }
    ctx.strokeStyle = '#ddd';
    ctx.stroke();
}

function drawCircle(x, y, color) {
    const centerX = x * cellSize + cellSize / 2;
    const centerY = y * cellSize + cellSize / 2;
    const radius = cellSize / 2.5;

    ctx.beginPath();
    ctx.arc(centerX, centerY, radius, 0, 2 * Math.PI, false);
    ctx.fillStyle = color;
    ctx.fill();
    ctx.lineWidth = 1;
    ctx.strokeStyle = '#003300';
    ctx.stroke();
}

function updateCanvas() {
    drawGrid();
    circles.forEach(circle => {
        drawCircle(circle.x, circle.y, circle.color);
    });
}

function getCircleAtPosition(x, y) {
    return circles.find(circle => circle.x === x && circle.y === y);
}

canvas.addEventListener('click', (event) => {
    const rect = canvas.getBoundingClientRect();
    const x = Math.floor((event.clientX - rect.left) / cellSize);
    const y = Math.floor((event.clientY - rect.top) / cellSize);
    const existingCircle = getCircleAtPosition(x, y);

    if (existingCircle) {
        circles = circles.filter(circle => !(circle.x === x && circle.y === y));
    } else {
        const color = document.getElementById('circleColor').value;
        circles.push({ x, y, color });
    }

    updateCanvas();
});

document.getElementById('addCircle').addEventListener('click', () => {
    const x = Math.floor(Math.random() * gridSize);
    const y = Math.floor(Math.random() * gridSize);
    const color = document.getElementById('circleColor').value;
    circles.push({ x, y, color });
    updateCanvas();
});

document.getElementById('deleteCircle').addEventListener('click', () => {
    const x = Math.floor(Math.random() * gridSize);
    const y = Math.floor(Math.random() * gridSize);
    circles = circles.filter(circle => !(circle.x === x && circle.y === y));
    updateCanvas();
});

drawGrid();
