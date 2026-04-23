<template>
  <div class="loader-wrapper">
    <div class="spinner"></div>
  </div>
</template>

<style scoped>
.loader-wrapper {
  display: flex;
  justify-content: center;
  padding: 20px 0;
}

.spinner {
  width: 28px;
  height: 28px;
  border: 3px solid var(--color-border);
  border-top: 3px solid var(--color-primary);
  border-radius: 50%;
  animation: spin 0.3s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
</style>