<script lang="ts">
  import { onMount } from "svelte";

  // Live video stream
  const videoSrc = "http://localhost:8000/video";

  // Info panel data
  interface DetectedObject {
    bbox: number[];
    confidence: number;
    class: number;
  }

  interface DetectionData {
    fps: number;
    objects: DetectedObject[];
  }

  let info: DetectionData = { fps: 0, objects: [] };

  // Audio setup
  let userReady = false;
  const screamSounds = [
    "/scream-1.wav",
    "/scream-2.wav",
    "/scream-3.wav",
    "/scream-4.wav"
  ];

  let screamAlert = false;

  function enableSound() {
    userReady = true;
    screamAlert = false;
  }

  function playRandomScream() {
    if (!userReady) return;

    screamAlert = true;

    const audioFile = screamSounds[Math.floor(Math.random() * screamSounds.length)];
    const audio = new Audio(audioFile);
    audio.play().catch(e => console.error("Audio play error:", e));

    // Hide alert after 2 seconds
    setTimeout(() => {
      screamAlert = false;
    }, 2000);
  }

  async function fetchDetections() {
    try {
      const res = await fetch("http://localhost:8000/detections");
      if (!res.ok) throw new Error("Backend not ready");
      const data: DetectionData = await res.json();
      info = data;

      // Trigger sound if any object has confidence >= 0.85
      const alertTriggered = info.objects.some(obj => obj.confidence >= 0.75);
      if (alertTriggered) playRandomScream();
    } catch (err) {
      console.error("Error fetching detections:", err);
    }
  }

  // Fetch detections every 1 second
  let interval: number;
  onMount(() => {
    interval = setInterval(fetchDetections, 1000);
    return () => clearInterval(interval);
  });
</script>

<main>
  <div class="container">
    <!-- Left: Info -->
    <div class="info">
      <h2>YOLO Info Panel</h2>
      <p>Last Update: {new Date().toLocaleTimeString()}</p>
      <ul>
        <li>FPS: {info.fps}</li>
        <li>Objects Detected: {info.objects.length}</li>
        {#each info.objects as obj, i (i)}
          <li>
            Object {i + 1}: Class {obj.class}, Confidence {obj.confidence.toFixed(2)},
            BBox [{obj.bbox.map(n => n.toFixed(1)).join(", ")}]
          </li>
        {/each}
      </ul>

      {#if !userReady}
        <button on:click={enableSound} class="enable-sound-btn">
          Enable Sound Alerts
        </button>
      {/if}

      {#if screamAlert}
        <div class="scream-alert">SCREAM ALERT!</div>
      {/if}
    </div>

    <!-- Right: Live Video -->
    <div class="video">
      <h2>Live Video</h2>
      <img src={videoSrc} alt="Live YOLO Stream" />
    </div>
  </div>
</main>

<style>
  main {
    padding: 2rem;
    font-family: sans-serif;
  }

  .container {
    display: flex;
    gap: 2rem;
    justify-content: center;
    align-items: flex-start;
  }

  .info {
    flex: 1;
    background-color: #f5f5f5;
    padding: 1rem;
    border-radius: 8px;
    max-width: 400px;
    position: relative;
  }

  .video {
    flex: 2;
    text-align: center;
  }

  .video img {
    width: 100%;
    max-width: 640px;
    border: 2px solid #333;
    border-radius: 8px;
  }

  ul {
    padding-left: 1rem;
  }

  li {
    margin-bottom: 0.5rem;
    font-size: 0.9rem;
  }

  .enable-sound-btn {
    margin-top: 1rem;
    padding: 0.5rem 1rem;
    font-size: 1rem;
    border-radius: 5px;
    cursor: pointer;
  }

  .scream-alert {
    position: absolute;
    top: 0;
    right: 0;
    background-color: red;
    color: white;
    padding: 0.5rem 1rem;
    font-weight: bold;
    border-radius: 0 0 0 8px;
  }
</style>
