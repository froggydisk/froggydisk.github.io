import * as THREE from "three";

const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(
  75,
  window.innerWidth / window.innerHeight,
  0.1,
  1000
);
const renderer = new THREE.WebGLRenderer({
  canvas: document.getElementById("canvas"),
  antialias: true,
});
renderer.setSize(canvas.clientWidth, canvas.clientHeight);
renderer.setClearColor(0x131418);
document.body.appendChild(renderer.domElement);

const geometry = new THREE.BufferGeometry();
const vertices = new Float32Array(500 * 3);

for (let i = 0; i < vertices.length; i += 3) {
  const [x, y, z] = randomInSphere(1.5);
  vertices[i] = x;
  vertices[i + 1] = y;
  vertices[i + 2] = z;
}

geometry.setAttribute("position", new THREE.BufferAttribute(vertices, 3));

const material = new THREE.PointsMaterial({
  color: 0xffffff,
  size: 0.005,
  transparent: true,
});

const points = new THREE.Points(geometry, material);
scene.add(points);

camera.position.z = 1;

function animate() {
  requestAnimationFrame(animate);

  points.rotation.x -= 0.001;
  points.rotation.y -= 0.00067;

  renderer.render(scene, camera);
}

animate();

function randomInSphere(radius) {
  let x, y, z, d;
  do {
    x = Math.random() * 2 - 1;
    y = Math.random() * 2 - 1;
    z = Math.random() * 2 - 1;
    d = x * x + y * y + z * z;
  } while (d > 1);
  const scale = radius / Math.sqrt(d);
  return [x * scale, y * scale, z * scale];
}

window.addEventListener("resize", () => {
  const width = container.clientWidth;
  const height = container.clientHeight;
  renderer.setSize(width, height);
  camera.aspect = width / height;
  camera.updateProjectionMatrix();
});
